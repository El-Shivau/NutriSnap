"""
WSGI Entry Point
================

This module is the entry point used by Gunicorn (and Flask's CLI) to
locate the Flask application object.

Development usage:

    flask --app backend.wsgi run --debug

Production usage (Gunicorn):

    gunicorn --workers 4 --bind 0.0.0.0:8000 backend.wsgi:app
"""

import os

from backend.app import create_app

# Determine environment from the FLASK_ENV variable (default: development)
config_name = os.environ.get("FLASK_ENV", "development")

app = create_app(config_name)

if __name__ == "__main__":
    # This block is only reached when running directly with `python backend/wsgi.py`
    # For normal use, call via `flask --app backend.wsgi run`
    app.run()
