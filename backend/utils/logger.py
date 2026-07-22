"""
Centralised Logging Setup
==========================

Provides a single configure_logging() function that is called once
inside create_app(). All modules should use:

    import logging
    logger = logging.getLogger(__name__)

This ensures all log messages flow through the same handlers and
formatter regardless of where they originate.

Log Destinations
----------------
1. Console (StreamHandler) — always active, coloured in development.
2. Rotating File (RotatingFileHandler) — logs to logs/nutrisnap.log,
   rotates at 10 MB, keeps 5 backups.

Log Format
----------
[TIMESTAMP] [LEVEL] [module_name] - message

Example
-------
[2024-01-15 10:30:00] [INFO] [backend.services.auth_service] - User registered: alice@example.com
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask


def configure_logging(app: Flask) -> None:
    """
    Configure application-wide logging based on app config.

    Attaches a console handler (always) and a rotating file handler
    (when not in testing mode).

    Parameters
    ----------
    app : Flask
        The Flask application instance.
    """
    log_level_str: str = app.config.get("LOG_LEVEL", "INFO")
    log_level: int = getattr(logging, log_level_str.upper(), logging.INFO)
    log_file: str = app.config.get("LOG_FILE", "logs/nutrisnap.log")

    # Remove Flask's default handlers to avoid duplicate output
    app.logger.handlers.clear()

    # Shared formatter for all handlers
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Console Handler
    # ------------------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ------------------------------------------------------------------
    # Rotating File Handler (skip in testing to avoid creating log files)
    # ------------------------------------------------------------------
    file_handler: RotatingFileHandler | None = None
    if not app.config.get("TESTING", False):
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

    # ------------------------------------------------------------------
    # Apply to the root logger so ALL modules inherit these settings
    # ------------------------------------------------------------------
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)

    # Also apply to Flask's own logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    if file_handler:
        app.logger.addHandler(file_handler)

    app.logger.info("Logging configured. Level: %s | File: %s", log_level_str, log_file)
