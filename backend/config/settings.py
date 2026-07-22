"""
Application Configuration
==========================

Defines configuration classes for different environments.
The correct class is selected by the FLASK_ENV environment variable
and loaded inside the create_app() factory.

Classes
-------
- Config          : Base configuration shared across all environments.
- DevelopmentConfig : Development overrides (debug on, SQLite).
- ProductionConfig  : Production overrides (debug off, secure settings).
- TestingConfig     : Testing overrides (in-memory DB, CSRF off).

Environment Variables Required
------------------------------
FLASK_SECRET_KEY    : Secret key for session signing (required in prod).
DATABASE_URL        : SQLAlchemy database URI.
MODEL_PATH          : Path to the trained Keras model file.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Base configuration — values shared across all environments."""

    # -------------------------------------------------------------------------
    # Flask Core
    # -------------------------------------------------------------------------
    SECRET_KEY: str = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "sqlite:///nutrisnap.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False  # Suppress deprecation warning

    # -------------------------------------------------------------------------
    # File Upload
    # -------------------------------------------------------------------------
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "backend/uploads")
    ALLOWED_EXTENSIONS: set = {
        ext.strip() for ext in os.environ.get("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp").split(",")
    }

    # -------------------------------------------------------------------------
    # Machine Learning
    # -------------------------------------------------------------------------
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "ml/models/food101_v1.keras")
    TOP_K_PREDICTIONS: int = int(os.environ.get("TOP_K_PREDICTIONS", 3))

    # -------------------------------------------------------------------------
    # Security
    # -------------------------------------------------------------------------
    BCRYPT_LOG_ROUNDS: int = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))
    WTF_CSRF_ENABLED: bool = True

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.environ.get("LOG_FILE", "logs/nutrisnap.log")


class DevelopmentConfig(Config):
    """Development configuration — debug mode on, SQLite database."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "sqlite:///nutrisnap_dev.db")
    BCRYPT_LOG_ROUNDS: int = 4  # Faster hashing during development
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Config):
    """Production configuration — debug off, strong secret key required."""

    DEBUG: bool = False
    TESTING: bool = False

    @classmethod
    def init_app(cls, app) -> None:  # type: ignore[override]
        """Additional production-specific initialisation."""
        Config.init_app(app)

        # Ensure a strong secret key is set in production
        assert os.environ.get("FLASK_SECRET_KEY"), (
            "FLASK_SECRET_KEY environment variable must be set in production!"
        )


class TestingConfig(Config):
    """Testing configuration — in-memory database, CSRF protection off."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False  # Disable CSRF in tests for simplicity
    BCRYPT_LOG_ROUNDS: int = 4  # Faster hashing in tests


# Mapping from FLASK_ENV string to configuration class
config_map: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
