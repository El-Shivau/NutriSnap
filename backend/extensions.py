"""
Flask Extension Instances
=========================

All shared Flask extensions are instantiated here — without being bound to
a specific Flask app. They are wired to the real app inside create_app()
using the init_app() pattern. This avoids circular imports across modules.

Usage
-----
Import from this module wherever an extension is needed:

    from backend.extensions import db, login_manager, bcrypt
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy ORM instance — used in all model definitions
db: SQLAlchemy = SQLAlchemy()

# Flask-Login session manager — handles user authentication state
login_manager: LoginManager = LoginManager()

# Flask-Bcrypt — provides password hashing utilities
bcrypt: Bcrypt = Bcrypt()
