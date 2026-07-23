"""
Food Controller
===============

Handles HTTP requests for food recognition and logging:
  - GET  /food/upload          → Display image upload form
  - POST /food/upload          → Receive image, run ML prediction, show results
  - GET  /food/prediction      → Show prediction results (session-guarded)
  - POST /food/log             → Save a confirmed food log entry (ACID)
  - GET  /food/history         → Display the user's food log history
  - GET  /food/uploads/<file>  → Serve uploaded images (owner-only)

Security model
--------------
Every route is decorated with @login_required.
Uploaded images are served only to the user who owns them — the filename
UUID prefix is checked against food_log records for the current user, so
an attacker who guesses a filename still gets a 403.
Session data (last_prediction, last_nutrition) is signed by Flask using
the FLASK_SECRET_KEY, so it cannot be tampered with by the client.
"""

import logging
import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required

from backend.services.food_service import FoodService

logger = logging.getLogger(__name__)

food_bp = Blueprint("food", __name__)
_food_service = FoodService()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_upload_folder() -> str:
    """Return the absolute path to the uploads directory."""
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return os.path.join(
        project_root,
        current_app.config.get("UPLOAD_FOLDER", "backend/uploads"),
    )


# ---------------------------------------------------------------------------
# Serve uploaded images — owner-only access
# ---------------------------------------------------------------------------

@food_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    """
    Serve an uploaded image.

    Security: only the user who owns the image (i.e. has a food_log row
    with this filename) may download it.  Anyone who guesses a UUID filename
    but doesn't own it gets a 404 (not 403, to avoid confirming existence).
    """
    # Check that at least one of this user's food logs references the file
    from backend.repositories.food_log_repository import FoodLogRepository
    repo = FoodLogRepository()
    if not repo.user_owns_image(current_user.id, filename):
        abort(404)

    upload_folder = _get_upload_folder()
    return send_from_directory(upload_folder, filename)


# ---------------------------------------------------------------------------
# Upload & predict
# ---------------------------------------------------------------------------

@food_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """
    Display the image upload form (GET) or handle file submission (POST).

    On POST:
      1. Validates file extension.
      2. Saves file to uploads/ with a UUID prefix (prevents enumeration).
      3. Runs the ML predictor.
      4. Looks up nutritional data.
      5. Stores results in the signed Flask session (not in the URL).
      6. Redirects to /food/prediction.
    """
    if request.method == "GET":
        return render_template("food/upload.html", title="Upload Food Image")

    # --- POST ---
    file = request.files.get("image")

    if not file or file.filename == "":
        flash("Please select an image file to upload.", "warning")
        return redirect(url_for("food.upload"))

    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})
    if not _food_service.validate_image_file(file.filename, allowed):
        flash(
            f"Invalid file type. Allowed formats: {', '.join(sorted(allowed)).upper()}",
            "danger",
        )
        return redirect(url_for("food.upload"))

    upload_folder = _get_upload_folder()

    try:
        filename = _food_service.save_image(file, upload_folder)
    except Exception as exc:
        logger.error("Failed to save uploaded image: %s", exc)
        flash("Failed to save your image. Please try again.", "danger")
        return redirect(url_for("food.upload"))

    image_path = os.path.join(upload_folder, filename)
    try:
        prediction = _food_service.predict_food(image_path)
    except Exception as exc:
        logger.error("Prediction failed: %s", exc)
        flash(
            "The AI model could not process your image. Please try a clearer photo.",
            "warning",
        )
        return redirect(url_for("food.upload"))

    # Nutrition lookup — provide a zeroed fallback so the prediction page
    # always renders even if a food isn't in the nutrition table yet.
    nutrition = _food_service.get_nutrition(prediction["food_name"]) or {
        "food_name": prediction["food_name"],
        "display_name": prediction["display_name"],
        "calories": 0,
        "protein_g": 0,
        "fat_g": 0,
        "carbs_g": 0,
        "fiber_g": 0,
        "serving_size_g": 100,
        "notes": None,
    }

    # Store in signed session — client cannot forge or read these values
    session["last_prediction"] = prediction
    session["last_nutrition"] = nutrition
    session["last_image_filename"] = filename
    # Bind the scan to the current user so another user can't steal the session
    session["last_scan_user_id"] = current_user.id

    return redirect(url_for("food.prediction"))


# ---------------------------------------------------------------------------
# Show prediction results
# ---------------------------------------------------------------------------

@food_bp.route("/prediction")
@login_required
def prediction():
    """
    Show the ML prediction results.

    Enforces that the session data belongs to the currently logged-in user.
    """
    pred = session.get("last_prediction")
    nutrition = session.get("last_nutrition")
    image_filename = session.get("last_image_filename")
    scan_user_id = session.get("last_scan_user_id")

    if not pred:
        flash("No prediction found. Please upload an image first.", "info")
        return redirect(url_for("food.upload"))

    # User-binding check: if someone else's session somehow leaks, reject it
    if scan_user_id != current_user.id:
        session.pop("last_prediction", None)
        session.pop("last_nutrition", None)
        session.pop("last_image_filename", None)
        session.pop("last_scan_user_id", None)
        flash("Session mismatch. Please scan a new image.", "warning")
        return redirect(url_for("food.upload"))

    return render_template(
        "food/prediction.html",
        title="Prediction Results",
        prediction=pred,
        nutrition=nutrition,
        image_filename=image_filename,
    )


# ---------------------------------------------------------------------------
# Confirm and save food log (ACID)
# ---------------------------------------------------------------------------

@food_bp.route("/log", methods=["POST"])
@login_required
def log_food():
    """
    Save the confirmed food log entry to the database.

    ACID guarantees:
    - Atomicity  : food_log INSERT and leaderboard UPDATE happen in the same
                   DB transaction inside create_food_log().
    - Consistency: FoodLog FK to users.id enforced at DB level.
    - Isolation  : SQLAlchemy session-level locking; leaderboard row is
                   read → modified → committed in a single transaction.
    - Durability : Supabase PostgreSQL with WAL enabled.

    Security: the food log is always written under current_user.id — the
    client cannot supply a different user_id.
    """
    pred = session.get("last_prediction")
    nutrition = session.get("last_nutrition")
    image_filename = session.get("last_image_filename")
    scan_user_id = session.get("last_scan_user_id")

    if not pred or not nutrition:
        flash("Session expired. Please upload a new image.", "warning")
        return redirect(url_for("food.upload"))

    # Prevent cross-user session replay
    if scan_user_id != current_user.id:
        flash("Session mismatch. Please scan a new image.", "warning")
        return redirect(url_for("food.upload"))

    notes = request.form.get("notes", "").strip() or None

    try:
        _food_service.create_food_log(
            user_id=current_user.id,   # always the authenticated user
            prediction=pred,
            nutrition=nutrition,
            image_filename=image_filename,
            notes=notes,
        )
    except Exception as exc:
        logger.error("Failed to save food log for user %d: %s", current_user.id, exc)
        flash("Failed to save food log. Please try again.", "danger")
        return redirect(url_for("food.prediction"))

    # Clear session data only after successful DB commit
    session.pop("last_prediction", None)
    session.pop("last_nutrition", None)
    session.pop("last_image_filename", None)
    session.pop("last_scan_user_id", None)

    flash(f"'{pred['display_name']}' added to your food log!", "success")
    return redirect(url_for("food.history"))


# ---------------------------------------------------------------------------
# Food history
# ---------------------------------------------------------------------------

@food_bp.route("/history")
@login_required
def history():
    """
    Display the current user's food log history and today's nutritional totals.

    Data is always scoped to current_user.id — users can only see their own logs.
    """
    logs = _food_service.get_user_history(current_user.id, limit=50)
    today_summary = _food_service.get_today_summary(current_user.id)

    return render_template(
        "food/history.html",
        title="My Food History",
        logs=logs,
        today_summary=today_summary,
    )
