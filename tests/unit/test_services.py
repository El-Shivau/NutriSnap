"""
Unit Tests — Validators
========================

Tests for pure validation functions in backend/utils/validators.py.
These tests require NO Flask app context since validators are pure functions.
"""

import pytest
from backend.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_image_extension,
)


class TestEmailValidator:
    def test_valid_email(self):
        ok, err = validate_email("user@example.com")
        assert ok is True
        assert err is None

    def test_invalid_email_no_at(self):
        ok, err = validate_email("userexample.com")
        assert ok is False
        assert err is not None

    def test_empty_email(self):
        ok, err = validate_email("")
        assert ok is False

    def test_email_too_long(self):
        long_email = "a" * 115 + "@b.com"
        ok, err = validate_email(long_email)
        assert ok is False


class TestUsernameValidator:
    def test_valid_username(self):
        ok, err = validate_username("john_doe")
        assert ok is True

    def test_too_short(self):
        ok, err = validate_username("ab")
        assert ok is False

    def test_too_long(self):
        ok, err = validate_username("a" * 31)
        assert ok is False

    def test_starts_with_number(self):
        ok, err = validate_username("1john")
        assert ok is False

    def test_special_chars(self):
        ok, err = validate_username("john@doe")
        assert ok is False


class TestPasswordValidator:
    def test_valid_password(self):
        ok, err = validate_password("SecurePass1")
        assert ok is True

    def test_too_short(self):
        ok, err = validate_password("Abc1")
        assert ok is False

    def test_no_uppercase(self):
        ok, err = validate_password("password123")
        assert ok is False

    def test_no_digit(self):
        ok, err = validate_password("PasswordOnly")
        assert ok is False


class TestImageExtensionValidator:
    ALLOWED = {"png", "jpg", "jpeg", "webp"}

    def test_valid_png(self):
        assert validate_image_extension("food.png", self.ALLOWED) is True

    def test_valid_jpeg(self):
        assert validate_image_extension("meal.JPEG", self.ALLOWED) is True

    def test_invalid_extension(self):
        assert validate_image_extension("virus.exe", self.ALLOWED) is False

    def test_no_extension(self):
        assert validate_image_extension("noextension", self.ALLOWED) is False
