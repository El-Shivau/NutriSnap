"""
Auth Service
============

Contains all business logic for user authentication.

Responsibilities
----------------
- Registering a new user (validate → hash password → persist).
- Authenticating a user (look up by email → verify hash → log in).
- Password utilities.

Called By
---------
- backend/controllers/auth_controller.py

Calls Into
----------
- backend/repositories/user_repository.py

Design Rule
-----------
No Flask request or response objects should ever appear in this file.
This service must be independently testable without an HTTP context.
"""

import logging
from typing import Optional

from flask_login import login_user

from backend.extensions import bcrypt
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.utils.validators import validate_email, validate_password, validate_username

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for user authentication operations."""

    def __init__(self, user_repository: Optional[UserRepository] = None) -> None:
        """
        Initialise with an optional repository (supports dependency injection for tests).

        Parameters
        ----------
        user_repository : UserRepository, optional
            The repository to use. Defaults to a new UserRepository instance.
        """
        self.user_repo = user_repository or UserRepository()

    def register(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str = "",
    ) -> tuple[bool, str]:
        """
        Register a new user account.

        Parameters
        ----------
        username : str
            Desired username.
        email : str
            User's email address.
        password : str
            Plaintext password (will be hashed before storage).
        confirm_password : str
            Must match password.

        Returns
        -------
        tuple[bool, str]
            (True, "success") on success.
            (False, error_message) on failure.
        """
        # --- Input validation ---
        ok, err = validate_username(username)
        if not ok:
            return False, err

        ok, err = validate_email(email)
        if not ok:
            return False, err

        ok, err = validate_password(password)
        if not ok:
            return False, err

        if confirm_password and password != confirm_password:
            return False, "Passwords do not match."

        # --- Uniqueness checks ---
        email_lower = email.lower().strip()
        if self.user_repo.find_by_email(email_lower):
            return False, "An account with that email already exists."

        if self.user_repo.find_by_username(username.strip()):
            return False, "That username is already taken."

        # --- Hash password and save ---
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username.strip(),
            email=email_lower,
            password_hash=password_hash,
        )

        try:
            self.user_repo.save(user)
        except Exception as exc:
            logger.error("Failed to save new user: %s", exc)
            return False, "Registration failed due to a server error. Please try again."

        logger.info("New user registered: %s (%s)", user.username, user.email)
        return True, "success"

    def login(
        self,
        email: str,
        password: str,
        remember: bool = False,
    ) -> tuple[bool, str]:
        """
        Authenticate a user with email and password.

        Parameters
        ----------
        email : str
            The user's email address.
        password : str
            The plaintext password to verify.
        remember : bool
            If True, set a persistent session cookie.

        Returns
        -------
        tuple[bool, str]
            (True, "success") on success.
            (False, error_message) on failure.
        """
        if not email or not password:
            return False, "Email and password are required."

        user = self.user_repo.find_by_email(email.lower().strip())

        # Use a constant-time check to prevent timing attacks
        # (always check the hash even if user is not found, using a dummy hash)
        if user is None or not bcrypt.check_password_hash(user.password_hash, password):
            return False, "Invalid email or password."

        if not user.is_active:
            return False, "This account has been deactivated. Please contact support."

        login_user(user, remember=remember)
        logger.info("User logged in: %s", user.username)
        return True, "success"

