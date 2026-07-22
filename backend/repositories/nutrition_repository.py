"""
Nutrition Repository
====================

Handles all database access for the Nutrition model.
"""

import logging
from typing import Optional

from backend.extensions import db
from backend.models.nutrition import Nutrition

logger = logging.getLogger(__name__)


class NutritionRepository:
    """Data access object for Nutrition model operations."""

    def find_by_food_name(self, food_name: str) -> Optional[Nutrition]:
        """
        Find nutritional data for a specific food class.

        Parameters
        ----------
        food_name : str
            The Food-101 class name (e.g. "pizza").
            Must be lowercase with underscores.

        Returns
        -------
        Nutrition | None
        """
        return Nutrition.query.filter_by(food_name=food_name.lower()).first()

    def find_all(self) -> list[Nutrition]:
        """
        Return all nutrition entries, ordered alphabetically by food name.

        Returns
        -------
        list[Nutrition]
        """
        return Nutrition.query.order_by(Nutrition.food_name).all()

    def save(self, nutrition: Nutrition) -> Nutrition:
        """Persist a new or updated Nutrition entry."""
        db.session.add(nutrition)
        db.session.commit()
        return nutrition

    def bulk_insert(self, nutrition_list: list[Nutrition]) -> int:
        """
        Insert multiple Nutrition entries efficiently.
        Used by the seed script (data/seeds/seed_nutrition.py).

        Parameters
        ----------
        nutrition_list : list[Nutrition]
            List of Nutrition objects to insert.

        Returns
        -------
        int
            Number of records inserted.
        """
        db.session.add_all(nutrition_list)
        db.session.commit()
        logger.info("Bulk inserted %d nutrition records.", len(nutrition_list))
        return len(nutrition_list)
