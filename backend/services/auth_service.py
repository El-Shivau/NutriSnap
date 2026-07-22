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

        Returns
        -------
        tuple[bool, str]
            (True, "success") on success.
            (False, error_message) on failure.
        """
        # TODO: Implement in Phase 5
        # 1. Check if email is already registered.
        # 2. Check if username is already taken.
        # 3. Hash the password.
        # 4. Create and persist the User via user_repository.
        # 5. Return success.
        raise NotImplementedError("AuthService.register() — implemented in Phase 5")

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
        # TODO: Implement in Phase 5
        # 1. Find the user by email.
        # 2. Verify bcrypt hash.
        # 3. Call login_user() from Flask-Login.
        # 4. Return success.
        raise NotImplementedError("AuthService.login() — implemented in Phase 5")
