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

Called By
---------
- backend/controllers/food_controller.py

Calls Into
----------
- backend/repositories/food_log_repository.py
- backend/repositories/nutrition_repository.py
- ml/inference/predictor.py  (via a wrapper — never directly in Flask)

Design Rule
-----------
No TensorFlow or Keras imports should appear in this file.
All ML calls go through the Predictor class from ml/inference/predictor.py.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FoodService:
    """Service class for food recognition and food log management."""

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
        # TODO: Implement in Phase 7
        raise NotImplementedError("FoodService.validate_image_file() — implemented in Phase 7")

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
        # TODO: Implement in Phase 7
        raise NotImplementedError("FoodService.save_image() — implemented in Phase 7")

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
              "confidence": float,        # Top-1 confidence (0.0–1.0)
              "top_3": [                  # Top-3 predictions
                {"food_name": str, "confidence": float},
                ...
              ]
            }
        """
        # TODO: Implement in Phase 7 — calls ml.inference.predictor.Predictor
        raise NotImplementedError("FoodService.predict_food() — implemented in Phase 7")

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

        Parameters
        ----------
        user_id : int
            The authenticated user's ID.
        prediction : dict
            Output of predict_food().
        nutrition : dict
            Output of NutritionService.get_by_food_name().
        image_filename : str, optional
            Filename of the uploaded image.
        notes : str, optional
            Any notes the user added.

        Returns
        -------
        dict
            The serialised FoodLog entry (via FoodLog.to_dict()).
        """
        # TODO: Implement in Phase 7
        raise NotImplementedError("FoodService.create_food_log() — implemented in Phase 7")
