"""
Unit Tests — Models
====================

Tests for SQLAlchemy ORM models. These tests verify:
  - Model fields are correctly defined.
  - Relationships work as expected.
  - to_dict() methods return correct data.
  - Constraint violations raise appropriate errors.
"""

import pytest
from datetime import datetime


class TestUserModel:
    """Tests for the User model."""

    def test_user_creation(self, db):
        """A User can be created and saved to the database."""
        from backend.extensions import bcrypt
        from backend.models.user import User

        user = User(
            username="alice",
            email="alice@example.com",
            password_hash=bcrypt.generate_password_hash("Secret123").decode("utf-8"),
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)

    def test_user_to_dict_excludes_password(self, db):
        """to_dict() must NOT include password_hash."""
        from backend.extensions import bcrypt
        from backend.models.user import User

        user = User(
            username="bob",
            email="bob@example.com",
            password_hash=bcrypt.generate_password_hash("Secret123").decode("utf-8"),
        )
        db.session.add(user)
        db.session.commit()

        d = user.to_dict()
        assert "password_hash" not in d
        assert d["username"] == "bob"
        assert d["email"] == "bob@example.com"

    def test_duplicate_email_raises_error(self, db):
        """Two users with the same email should raise an IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        from backend.extensions import bcrypt
        from backend.models.user import User

        hash_ = bcrypt.generate_password_hash("Secret123").decode("utf-8")
        user1 = User(username="charlie", email="same@example.com", password_hash=hash_)
        user2 = User(username="dave", email="same@example.com", password_hash=hash_)

        db.session.add(user1)
        db.session.commit()

        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()


class TestNutritionModel:
    """Tests for the Nutrition model."""

    def test_nutrition_creation(self, db):
        """A Nutrition record can be created and retrieved by food_name."""
        from backend.models.nutrition import Nutrition

        nutrition = Nutrition(
            food_name="pizza",
            display_name="Pizza",
            calories=266.0,
            protein_g=11.0,
            fat_g=10.0,
            carbs_g=33.0,
            fiber_g=2.3,
            serving_size_g=107.0,
        )
        db.session.add(nutrition)
        db.session.commit()

        fetched = Nutrition.query.filter_by(food_name="pizza").first()
        assert fetched is not None
        assert fetched.calories == 266.0
        assert fetched.display_name == "Pizza"

    def test_nutrition_to_dict(self, db):
        """to_dict() returns all expected keys."""
        from backend.models.nutrition import Nutrition

        nutrition = Nutrition(
            food_name="sushi",
            display_name="Sushi",
            calories=350.0,
            protein_g=18.0,
            fat_g=7.0,
            carbs_g=55.0,
            fiber_g=2.5,
            serving_size_g=200.0,
        )
        db.session.add(nutrition)
        db.session.commit()

        d = nutrition.to_dict()
        expected_keys = {
            "food_name", "display_name", "calories",
            "protein_g", "fat_g", "carbs_g", "fiber_g", "serving_size_g", "notes"
        }
        assert expected_keys == set(d.keys())


class TestFoodLogModel:
    """Tests for the FoodLog model."""

    def test_food_log_creation(self, db, test_user):
        """A FoodLog entry can be created and linked to a user."""
        from backend.models.food_log import FoodLog

        log = FoodLog(
            user_id=test_user.id,
            food_name="pizza",
            display_name="Pizza",
            confidence=0.92,
            calories=266.0,
            protein_g=11.0,
            fat_g=10.0,
            carbs_g=33.0,
            fiber_g=2.3,
            serving_size_g=107.0,
        )
        db.session.add(log)
        db.session.commit()

        assert log.id is not None
        assert log.user_id == test_user.id

    def test_food_log_to_dict_converts_confidence(self, db, test_user):
        """confidence in to_dict() should be expressed as a percentage."""
        from backend.models.food_log import FoodLog

        log = FoodLog(
            user_id=test_user.id,
            food_name="sushi",
            display_name="Sushi",
            confidence=0.875,
            calories=350.0,
            protein_g=18.0,
            fat_g=7.0,
            carbs_g=55.0,
            fiber_g=2.5,
            serving_size_g=200.0,
        )
        db.session.add(log)
        db.session.commit()

        d = log.to_dict()
        assert d["confidence"] == 87.5
