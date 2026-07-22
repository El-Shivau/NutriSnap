"""
Predictor — ML Inference Module
================================

This is the ONLY module that the Flask backend uses to interact with
the trained model. No TensorFlow code appears anywhere else in the
backend package.

The Predictor class:
  1. Loads the trained .keras model ONCE at startup (lazy loading).
  2. Preprocesses the input image using the shared preprocessor.
  3. Runs model.predict() to get class probabilities.
  4. Maps the class index to a human-readable food name.
  5. Returns the top-K predictions with confidence scores.

Usage (Phase 4 implementation)
-------------------------------
    from ml.inference.predictor import Predictor

    predictor = Predictor(model_path="ml/models/food101_v1.keras")

    result = predictor.predict("path/to/pizza.jpg")
    # Returns:
    # {
    #   "food_name": "pizza",
    #   "display_name": "Pizza",
    #   "confidence": 0.9342,
    #   "top_3": [
    #     {"food_name": "pizza",       "display_name": "Pizza",       "confidence": 0.9342},
    #     {"food_name": "focaccia",    "display_name": "Focaccia",    "confidence": 0.0412},
    #     {"food_name": "garlic_bread","display_name": "Garlic Bread","confidence": 0.0131},
    #   ]
    # }

IMPORTANT: Instantiate this class ONCE and reuse it. Loading a Keras
model is expensive (~1–2 seconds); you don't want to do it per request.
"""

import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# The 101 Food-101 class names in the order they appear after sorting
# (this must match the order used during training — tf.keras sorts alphabetically)
FOOD_CLASSES: list[str] = [
    "apple_pie", "baby_back_ribs", "baklava", "beef_carpaccio", "beef_tartare",
    "beet_salad", "beignets", "bibimbap", "bread_pudding", "breakfast_burrito",
    "bruschetta", "caesar_salad", "cannoli", "caprese_salad", "carrot_cake",
    "ceviche", "cheesecake", "cheese_plate", "chicken_curry", "chicken_quesadilla",
    "chicken_wings", "chocolate_cake", "chocolate_mousse", "churros", "clam_chowder",
    "club_sandwich", "crab_cakes", "creme_brulee", "croque_madame", "cup_cakes",
    "deviled_eggs", "donuts", "dumplings", "edamame", "eggs_benedict", "escargots",
    "falafel", "filet_mignon", "fish_and_chips", "foie_gras", "french_fries",
    "french_onion_soup", "french_toast", "fried_calamari", "fried_rice",
    "frozen_yogurt", "garlic_bread", "gnocchi", "greek_salad",
    "grilled_cheese_sandwich", "grilled_salmon", "guacamole", "gyoza",
    "hamburger", "hot_and_sour_soup", "hot_dog", "huevos_rancheros", "hummus",
    "ice_cream", "lasagna", "lobster_bisque", "lobster_roll_sandwich",
    "macaroni_and_cheese", "macarons", "miso_soup", "mussels", "nachos",
    "omelette", "onion_rings", "oysters", "pad_thai", "paella", "pancakes",
    "panna_cotta", "peking_duck", "pho", "pizza", "pork_chop", "poutine",
    "prime_rib", "pulled_pork_sandwich", "ramen", "ravioli", "red_velvet_cake",
    "risotto", "samosa", "sashimi", "scallops", "seaweed_salad",
    "shrimp_and_grits", "spaghetti_bolognese", "spaghetti_carbonara",
    "spring_rolls", "steak", "strawberry_shortcake", "sushi", "tacos",
    "takoyaki", "tiramisu", "tuna_tartare", "waffles",
]

assert len(FOOD_CLASSES) == 101, f"Expected 101 classes, got {len(FOOD_CLASSES)}"


def _class_name_to_display(class_name: str) -> str:
    """
    Convert a Food-101 class name to a human-readable display name.

    Example: 'apple_pie' → 'Apple Pie'
    """
    return class_name.replace("_", " ").title()


class Predictor:
    """
    Wraps the trained Keras model and provides a clean predict() interface.

    The model is loaded lazily — on the first call to predict() — so
    importing this class does not incur the loading overhead.
    """

    def __init__(self, model_path: Union[str, Path], top_k: int = 3) -> None:
        """
        Parameters
        ----------
        model_path : str | Path
            Path to the trained .keras model file.
            Example: 'ml/models/food101_v1.keras'
        top_k : int
            Number of top predictions to return. Default: 3.
        """
        self.model_path = Path(model_path)
        self.top_k = top_k
        self._model = None  # Loaded lazily on first predict() call

    def _load_model(self) -> None:
        """
        Load the Keras model from disk.

        Called automatically on the first predict() call.
        Subsequent calls reuse the cached model object.
        """
        # TODO: Implement in Phase 4
        raise NotImplementedError("Predictor._load_model() — implemented in Phase 4")

    def predict(self, image_source: Union[str, Path, bytes]) -> dict:
        """
        Run inference on a single image.

        Parameters
        ----------
        image_source : str | Path | bytes
            Path to an image file, or raw image bytes.

        Returns
        -------
        dict with keys:
            - food_name    : str   — Top-1 class name (e.g. 'pizza')
            - display_name : str   — Human-readable name (e.g. 'Pizza')
            - confidence   : float — Top-1 confidence score (0.0–1.0)
            - top_k        : list  — Top-K predictions, each with:
                             { food_name, display_name, confidence }

        Raises
        ------
        FileNotFoundError
            If a file path is given but the file does not exist.
        ValueError
            If the model file does not exist.
        RuntimeError
            If the model fails to make a prediction.
        """
        # TODO: Implement in Phase 4
        # 1. Load model if not already loaded.
        # 2. Preprocess image via ml.preprocessing.image_preprocessor.preprocess_image().
        # 3. Call model.predict(tensor).
        # 4. Get top-K indices and confidence scores.
        # 5. Map indices to FOOD_CLASSES names.
        # 6. Return structured result dict.
        raise NotImplementedError("Predictor.predict() — implemented in Phase 4")
