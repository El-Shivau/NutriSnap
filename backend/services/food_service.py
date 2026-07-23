"""
Food Service
============

Contains business logic for food recognition and logging.

Responsibilities
----------------
- Validating uploaded image files.
- Saving uploaded images to the uploads directory.
- Delegating to the ML inference module for predictions.
- Looking up nutritional data for a predicted food.
- Creating and saving FoodLog entries.
- Updating the weekly leaderboard when a new log is saved.

Called By
---------
- backend/controllers/food_controller.py

Calls Into
----------
- backend/repositories/food_log_repository.py
- backend/repositories/nutrition_repository.py
- backend/repositories/leaderboard_repository.py
- ml/inference/predictor.py  (via a lazy singleton — never imported at module level)

Design Rule
-----------
No TensorFlow or Keras imports should appear in this file.
All ML calls go through the Predictor class from ml/inference/predictor.py.
"""

import logging
import os
import uuid
from typing import Optional

from werkzeug.utils import secure_filename

from backend.models.food_log import FoodLog
from backend.repositories.food_log_repository import FoodLogRepository
from backend.repositories.leaderboard_repository import LeaderboardRepository
from backend.repositories.nutrition_repository import NutritionRepository

logger = logging.getLogger(__name__)

# Module-level singleton for the Predictor — loaded once, reused for every request.
# We use a lazy import so TensorFlow is only pulled in when the first prediction runs.
_predictor = None


def _get_predictor():
    """
    Return the module-level Predictor singleton.

    Lazy-initialises it on the first call using MODEL_PATH from the environment.
    """
    global _predictor
    if _predictor is None:
        model_path = os.environ.get("MODEL_PATH", "ml/models/food101_v1.pt")
        from ml.inference.predictor import Predictor
        _predictor = Predictor(model_path=model_path, top_k=3)
        logger.info("Predictor initialised with model: %s", model_path)
    return _predictor


class FoodService:
    """Service class for food recognition and food log management."""

    def __init__(self) -> None:
        self._food_log_repo = FoodLogRepository()
        self._nutrition_repo = NutritionRepository()
        self._leaderboard_repo = LeaderboardRepository()

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------

    def validate_image_file(self, filename: str, allowed_extensions: set) -> bool:
        """
        Check whether an uploaded filename has a permitted extension.

        Parameters
        ----------
        filename : str
            The original filename from the upload form.
        allowed_extensions : set
            Set of lowercase extension strings (e.g. {"png", "jpg", "jpeg"}).

        Returns
        -------
        bool
            True if the extension is allowed, False otherwise.
        """
        if not filename or "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in allowed_extensions

    def save_image(self, file, upload_folder: str) -> str:
        """
        Save an uploaded image file to the upload directory securely.

        Uses werkzeug.utils.secure_filename to prevent path traversal attacks.
        Adds a UUID prefix to avoid filename collisions.

        Parameters
        ----------
        file : FileStorage
            The uploaded file object from Flask's request.files.
        upload_folder : str
            Absolute path to the directory where images are stored.

        Returns
        -------
        str
            The saved filename (not the full path).
        """
        os.makedirs(upload_folder, exist_ok=True)

        original_name = secure_filename(file.filename or "upload.jpg")
        # Prepend UUID to prevent collisions
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        save_path = os.path.join(upload_folder, unique_name)

        file.save(save_path)
        logger.debug("Saved uploaded image: %s", save_path)
        return unique_name

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_food(self, image_path: str) -> dict:
        """
        Run the ML model on an image and return prediction results.

        Parameters
        ----------
        image_path : str
            Absolute path to the saved image file.

        Returns
        -------
        dict
            {
              "food_name": str,           # Top-1 predicted class
              "display_name": str,        # Human-readable name
              "confidence": float,        # Top-1 confidence (0.0-1.0)
              "top_k": [                  # Top-3 predictions
                {"food_name": str, "display_name": str, "confidence": float},
                ...
              ]
            }

        Raises
        ------
        RuntimeError
            If the predictor fails to load or run inference.
        """
        predictor = _get_predictor()
        result = predictor.predict(image_path)
        logger.info(
            "Prediction: %s (%.1f%% confidence)",
            result["display_name"],
            result["confidence"] * 100,
        )
        return result

    # ------------------------------------------------------------------
    # Nutrition lookup
    # ------------------------------------------------------------------

    def get_nutrition(self, food_name: str) -> Optional[dict]:
        """
        Look up nutritional data for a predicted food class name.

        Parameters
        ----------
        food_name : str
            The Food-101 class name (e.g. "pizza").

        Returns
        -------
        dict | None
            Nutrition data dict, or None if not found in the database.
        """
        nutrition = self._nutrition_repo.find_by_food_name(food_name)
        if nutrition is None:
            logger.warning("No nutrition data found for: %s", food_name)
            return None
        return nutrition.to_dict()

    # ------------------------------------------------------------------
    # Food Log
    # ------------------------------------------------------------------

    def create_food_log(
        self,
        user_id: int,
        prediction: dict,
        nutrition: dict,
        image_filename: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Create and persist a FoodLog entry for a confirmed prediction.

        Also updates the user's weekly leaderboard entry.

        Parameters
        ----------
        user_id : int
            The authenticated user's ID.
        prediction : dict
            Output of predict_food().
        nutrition : dict
            Output of get_nutrition().
        image_filename : str, optional
            Filename of the uploaded image.
        notes : str, optional
            Any notes the user added.

        Returns
        -------
        dict
            The serialised FoodLog entry (via FoodLog.to_dict()).
        """
        food_log = FoodLog(
            user_id=user_id,
            food_name=prediction["food_name"],
            display_name=prediction["display_name"],
            confidence=prediction["confidence"],
            # Snapshot nutrition values at log time
            calories=nutrition.get("calories", 0.0),
            protein_g=nutrition.get("protein_g", 0.0),
            fat_g=nutrition.get("fat_g", 0.0),
            carbs_g=nutrition.get("carbs_g", 0.0),
            fiber_g=nutrition.get("fiber_g", 0.0),
            serving_size_g=nutrition.get("serving_size_g", 100.0),
            image_filename=image_filename,
            notes=notes,
        )

        saved_log = self._food_log_repo.save(food_log)
        logger.info("Food log saved: user=%d food=%s", user_id, food_log.food_name)

        # Update weekly leaderboard
        try:
            week_start = self._leaderboard_repo.current_week_start()
            self._leaderboard_repo.upsert_user_score(
                user_id=user_id,
                week_start=week_start,
                calories=food_log.calories,
                protein_g=food_log.protein_g,
                carbs_g=food_log.carbs_g,
                fat_g=food_log.fat_g,
            )
        except Exception as exc:
            # Leaderboard update failure must never block saving the food log
            logger.error("Failed to update leaderboard: %s", exc)

        return saved_log.to_dict()

    def get_user_history(self, user_id: int, limit: int = 50) -> list[dict]:
        """
        Return a user's recent food log entries as a list of dicts.

        Parameters
        ----------
        user_id : int
        limit : int
            Maximum number of entries. Default: 50.

        Returns
        -------
        list[dict]
        """
        logs = self._food_log_repo.find_by_user(user_id, limit=limit)
        return [log.to_dict() for log in logs]

    def get_today_summary(self, user_id: int) -> dict:
        """
        Return today's nutritional totals for a user.

        Returns
        -------
        dict
            {
              "total_calories": float,
              "total_protein_g": float,
              "total_fat_g": float,
              "total_carbs_g": float,
              "log_count": int,
            }
        """
        logs = self._food_log_repo.find_today(user_id)
        return {
            "total_calories": round(sum(l.calories for l in logs), 1),
            "total_protein_g": round(sum(l.protein_g for l in logs), 1),
            "total_fat_g": round(sum(l.fat_g for l in logs), 1),
            "total_carbs_g": round(sum(l.carbs_g for l in logs), 1),
            "log_count": len(logs),
        }
