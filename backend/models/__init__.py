"""
Backend Models Package
======================

All SQLAlchemy ORM models are defined here and imported by the
application factory to ensure they are registered with the db metadata
before create_all() is called.
"""

from backend.models.food_log import FoodLog
from backend.models.friendship import Friendship
from backend.models.leaderboard import LeaderboardEntry
from backend.models.nutrition import Nutrition
from backend.models.user import User

__all__ = ["User", "FoodLog", "Nutrition", "Friendship", "LeaderboardEntry"]
