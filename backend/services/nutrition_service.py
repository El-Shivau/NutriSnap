"""
Nutrition Service
=================

Business logic for nutritional data lookup.

Responsibilities
----------------
- Retrieving nutritional information for a given food name.
- Listing all available foods in the database.

Called By
---------
- backend/controllers/food_controller.py (via FoodService)
- backend/controllers/dashboard_controller.py

Calls Into
----------
- backend/repositories/nutrition_repository.py
"""

import logging

from backend.repositories.nutrition_repository import NutritionRepository

logger = logging.getLogger(__name__)


class NutritionService:
    """Service class for nutritional data operations."""

    def __init__(self, nutrition_repository: NutritionRepository | None = None) -> None:
        self.nutrition_repo = nutrition_repository or NutritionRepository()

    def get_by_food_name(self, food_name: str) -> dict | None:
        """
        Retrieve nutritional data for a given food name.

        Parameters
        ----------
        food_name : str
            The Food-101 class name (e.g. "pizza", "pad_thai").

        Returns
        -------
        dict | None
            Nutritional data as a dictionary, or None if the food is not
            found in the database.
        """
        record = self.nutrition_repo.find_by_food_name(food_name)
        if record is None:
            logger.warning("No nutrition data found for: %s", food_name)
            return None
        return record.to_dict()

    def get_all_foods(self) -> list[dict]:
        """
        Return a list of all 101 food entries in the nutrition database.

        Returns
        -------
        list[dict]
            A list of nutritional dictionaries, one per food class.
        """
        records = self.nutrition_repo.find_all()
        return [r.to_dict() for r in records]
