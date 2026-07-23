"""
Flask Application Factory
==========================

The create_app() function is the single entry point for creating the
Flask application. Using a factory pattern instead of a global app object
enables:

  - Multiple app instances (one per test) without state leakage.
  - Clean environment-specific configuration.
  - Easier extension of the app without circular import issues.

Usage
-----
From the command line (development):

    flask --app backend.wsgi run --debug

From Python (e.g., tests):

    from backend.app import create_app
    app = create_app("testing")
"""

import os
from logging.handlers import RotatingFileHandler

from flask import Flask

from backend.config.settings import config_map
from backend.extensions import bcrypt, db, login_manager
from backend.utils.logger import configure_logging


def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Parameters
    ----------
    config_name : str, optional
        The configuration environment to use.
        One of: 'development', 'production', 'testing'.
        Defaults to the value of the FLASK_ENV environment variable,
        falling back to 'development'.

    Returns
    -------
    Flask
        A fully configured Flask application instance.
    """
    # Determine which config to use
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # Resolve template and static folders relative to the project root
    # so they live in frontend/ rather than inside the backend package.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "frontend", "templates"),
        static_folder=os.path.join(project_root, "frontend", "static"),
    )

    # Load configuration
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # -------------------------------------------------------------------------
    # Initialise extensions
    # -------------------------------------------------------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Redirect unauthenticated users to the login page
    login_manager.login_view = "auth.login"  # type: ignore[assignment]
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # -------------------------------------------------------------------------
    # Configure logging
    # -------------------------------------------------------------------------
    configure_logging(app)

    # -------------------------------------------------------------------------
    # Ensure upload directory exists
    # -------------------------------------------------------------------------
    upload_dir = os.path.join(project_root, app.config["UPLOAD_FOLDER"])
    os.makedirs(upload_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # Register blueprints
    # -------------------------------------------------------------------------
    _register_blueprints(app)

    # -------------------------------------------------------------------------
    # Register the user loader for Flask-Login
    # -------------------------------------------------------------------------
    _register_user_loader()

    app.logger.info("NutriSnap application started in '%s' mode.", config_name)

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints with the Flask app."""
    from backend.controllers.auth_controller import auth_bp
    from backend.controllers.dashboard_controller import dashboard_bp
    from backend.controllers.food_controller import food_bp
    from backend.controllers.friends_controller import friends_bp
    from backend.controllers.leaderboard_controller import leaderboard_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(food_bp, url_prefix="/food")
    app.register_blueprint(dashboard_bp)          # handles '/' and '/dashboard'
    app.register_blueprint(friends_bp)            # url_prefix set on the blueprint
    app.register_blueprint(leaderboard_bp)        # url_prefix set on the blueprint


def _register_user_loader() -> None:
    """Register the Flask-Login user loader callback."""
    from backend.models.user import User

    @login_manager.user_loader
    def load_user(user_id: str):  # type: ignore[return]
        """Load a user object by their integer ID stored in the session."""
        return db.session.get(User, int(user_id))
