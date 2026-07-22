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
        # TODO: Implement in Phase 5
        raise NotImplementedError("NutritionService.get_by_food_name() — implemented in Phase 5")

    def get_all_foods(self) -> list[dict]:
        """
        Return a list of all 101 food entries in the nutrition database.

        Returns
        -------
        list[dict]
            A list of nutritional dictionaries, one per food class.
        """
        # TODO: Implement in Phase 5
        raise NotImplementedError("NutritionService.get_all_foods() — implemented in Phase 5")
