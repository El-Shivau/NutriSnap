"""
Input Validators
================

Reusable validation functions used across the application.

These are pure functions — they take a value and return a result.
They have no dependency on Flask and can be used in tests directly.
"""

import re
from typing import Optional


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Check whether a string is a valid email address.

    Parameters
    ----------
    email : str
        The email address to validate.

    Returns
    -------
    tuple[bool, str | None]
        (True, None) if valid.
        (False, error_message) if invalid.
    """
    email = email.strip().lower()
    if not email:
        return False, "Email address is required."
    if len(email) > 120:
        return False, "Email address must not exceed 120 characters."
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Please enter a valid email address."
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Check whether a username meets NutriSnap's naming rules.

    Rules
    -----
    - 3 to 30 characters.
    - Letters, digits, underscores, and hyphens only.
    - Must start with a letter.

    Returns
    -------
    tuple[bool, str | None]
    """
    username = username.strip()
    if not username:
        return False, "Username is required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 30:
        return False, "Username must not exceed 30 characters."
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_\-]*$", username):
        return False, "Username must start with a letter and contain only letters, digits, underscores, or hyphens."
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Check whether a password meets NutriSnap's security requirements.

    Rules
    -----
    - Minimum 8 characters.
    - At least one uppercase letter.
    - At least one digit.

    Returns
    -------
    tuple[bool, str | None]
    """
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, None


def validate_image_extension(filename: str, allowed: set[str]) -> bool:
    """
    Return True if the filename has an allowed image extension.

    Parameters
    ----------
    filename : str
        The original filename from the upload form.
    allowed : set[str]
        Allowed extensions without the dot (e.g. {"png", "jpg", "jpeg"}).

    Returns
    -------
    bool
    """
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed
