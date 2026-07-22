"""
Food Controller
===============

Handles HTTP requests for food recognition and logging:
  - GET  /food/upload     → Display image upload form
  - POST /food/upload     → Receive and process uploaded image
  - GET  /food/prediction → Display prediction results
  - POST /food/log        → Save a confirmed food log entry
  - GET  /food/history    → Display the user's food log history

Controllers are intentionally thin — they only:
  1. Parse the incoming request.
  2. Call the appropriate service.
  3. Return an HTTP response.

All prediction and logging logic lives in backend/services/food_service.py.
"""

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

logger = logging.getLogger(__name__)

# Blueprint for all food-related routes
food_bp = Blueprint("food", __name__)


@food_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """
    Display the image upload form (GET) or handle file submission (POST).

    On POST:
      - Validates the uploaded file type and size.
      - Saves the file to the uploads directory.
      - Calls the food service to run the ML prediction.
      - Stores the prediction in the session.
      - Redirects to the prediction results page.
    """
    # Implementation will be completed in Phase 7
    return render_template("food/upload.html", title="Upload Food Image")


@food_bp.route("/prediction")
@login_required
def prediction():
    """
    Display the prediction results for the most recently uploaded image.

    Reads prediction data from the session (set by the upload route).
    Presents the top 3 predictions and nutritional information.
    """
    # Implementation will be completed in Phase 7
    return render_template("food/prediction.html", title="Prediction Results")


@food_bp.route("/log", methods=["POST"])
@login_required
def log_food():
    """
    Save a confirmed food log entry to the database.

    Called when the user clicks "Confirm & Save" on the prediction page.
    Redirects to the history page on success.
    """
    # Implementation will be completed in Phase 7
    flash("Food logged successfully!", "success")
    return redirect(url_for("food.history"))


@food_bp.route("/history")
@login_required
def history():
    """
    Display the user's complete food log history.
    """
    # Implementation will be completed in Phase 7
    return render_template("food/history.html", title="My Food History")
