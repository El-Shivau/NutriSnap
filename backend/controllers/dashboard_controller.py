"""
Dashboard Controller
====================

Handles HTTP requests for the landing page, dashboard, and user profile:
  - GET /              → Landing page (public)
  - GET /dashboard     → User dashboard (authenticated users only)
  - GET /profile       → User profile page
  - POST /profile      → Update profile information
"""

import logging

from flask import Blueprint, render_template
from flask_login import login_required

logger = logging.getLogger(__name__)

# Blueprint — no URL prefix, handles root-level routes
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """
    Landing page — publicly accessible.
    Shows the app description and call-to-action buttons.
    """
    return render_template("index.html", title="NutriSnap – AI Food Recognition")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Main dashboard — requires authentication.

    Displays:
      - Today's nutritional summary.
      - Recent food log entries.
      - Quick upload button.
    """
    # Implementation will be completed in Phase 6
    return render_template("dashboard/dashboard.html", title="Dashboard")


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    User profile page.

    GET  → Display current profile information.
    POST → Update username, bio, and avatar.
    """
    # Implementation will be completed in Phase 6
    return render_template("user/profile.html", title="My Profile")
