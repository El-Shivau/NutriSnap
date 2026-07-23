"""
Dashboard Controller
====================

Handles HTTP requests for the landing page, dashboard, and user profile:
  - GET  /           → Landing page (public)
  - GET  /dashboard  → User dashboard (authenticated, user-scoped data)
  - GET  /profile    → User profile (pre-populated with current user data)
  - POST /profile    → Update username / bio (validates ownership)
"""

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from backend.services.food_service import FoodService

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)
_food_service = FoodService()


@dashboard_bp.route("/")
def index():
    """Landing page — publicly accessible."""
    return render_template("index.html", title="NutriSnap – AI Food Recognition")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Main dashboard — requires authentication.

    All data is scoped to current_user.id so users can only see
    their own nutritional summary and recent logs.
    """
    today_summary = _food_service.get_today_summary(current_user.id)
    recent_logs = _food_service.get_user_history(current_user.id, limit=5)

    return render_template(
        "dashboard/dashboard.html",
        title="Dashboard",
        today_summary=today_summary,
        recent_logs=recent_logs,
    )


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    User profile page.

    GET  → Display current profile data pre-filled in the form.
    POST → Validate and save username/bio changes.

    Security: changes are always written to current_user — users
    cannot modify another user's profile by manipulating the request.
    """
    from backend.extensions import db
    from backend.models.user import User

    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        new_bio = request.form.get("bio", "").strip() or None

        # Validate username
        if not new_username or len(new_username) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return redirect(url_for("dashboard.profile"))

        if len(new_username) > 80:
            flash("Username must be 80 characters or fewer.", "danger")
            return redirect(url_for("dashboard.profile"))

        # Check uniqueness (excluding current user)
        existing = User.query.filter(
            User.username == new_username,
            User.id != current_user.id,
        ).first()
        if existing:
            flash("That username is already taken. Please choose another.", "danger")
            return redirect(url_for("dashboard.profile"))

        # Apply changes — always to the authenticated user only
        current_user.username = new_username
        current_user.bio = new_bio
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard.profile"))

    return render_template("user/profile.html", title="My Profile")
