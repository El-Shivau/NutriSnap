"""
Auth Controller
===============

Handles HTTP requests for user authentication:
  - GET  /auth/login     → Display login form
  - POST /auth/login     → Process login form
  - GET  /auth/register  → Display registration form
  - POST /auth/register  → Process registration form
  - GET  /auth/logout    → Log out the current user

Controllers are intentionally thin — they only:
  1. Parse the incoming request.
  2. Call the appropriate service.
  3. Return an HTTP response (redirect or render).

All business logic lives in backend/services/auth_service.py.
"""

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, logout_user, current_user

from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Blueprint for all authentication-related routes
auth_bp = Blueprint("auth", __name__)

# Single service instance (stateless — safe to share)
_auth_service = AuthService()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Display the login form (GET) or process login credentials (POST).

    On successful login, redirects to the dashboard.
    On failure, re-renders the form with an error flash message.
    """
    # Redirect already-authenticated users away from the login page
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        success, message = _auth_service.login(email, password, remember)

        if success:
            flash("Welcome back! You are now signed in.", "success")
            # Honour the 'next' param if present (safe redirect)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.dashboard"))
        else:
            flash(message, "danger")

    return render_template("auth/login.html", title="Login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Display the registration form (GET) or create a new user account (POST).

    On success, redirects to login page with a success message.
    On failure (e.g. duplicate email), re-renders with an error flash.
    """
    # Redirect already-authenticated users
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        success, message = _auth_service.register(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )

        if success:
            flash(
                "Account created successfully! Please sign in.",
                "success",
            )
            return redirect(url_for("auth.login"))
        else:
            flash(message, "danger")

    return render_template("auth/register.html", title="Register")


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log out the currently authenticated user and redirect to the landing page.
    """
    logout_user()
    flash("You have been logged out successfully.", "info")
    logger.info("User logged out.")
    return redirect(url_for("dashboard.index"))
