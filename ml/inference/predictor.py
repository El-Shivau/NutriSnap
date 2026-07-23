"""
Predictor -- ML Inference Module
================================

This is the ONLY module that the Flask backend uses to interact with
the trained model. No PyTorch code appears anywhere else in the
backend package.

The Predictor class:
  1. Loads the trained PyTorch model ONCE at startup (lazy loading).
  2. Preprocesses the input image using the shared preprocessor.
  3. Runs model.forward() to get class log-probabilities.
  4. Maps the class index to a human-readable food name.
  5. Returns the top-K predictions with confidence scores.

Model Strategy
--------------
We use a timm EfficientNetB0 model pre-trained on ImageNet-21k and
fine-tuned on Food-101. The model weights are stored as a .pt file
hosted on GitHub Releases and downloaded automatically via
MODEL_DOWNLOAD_URL in the environment.

When a trained .pt file is NOT available, the predictor falls back to
ImageNet-pretrained weights from timm's model hub. These will not
produce accurate Food-101 predictions -- they are a development
placeholder only.

Usage
-----
    from ml.inference.predictor import Predictor

    predictor = Predictor()
    result = predictor.predict("path/to/pizza.jpg")
    # Returns:
    # {
    #   "food_name": "pizza",
    #   "display_name": "Pizza",
    #   "confidence": 0.9342,
    #   "top_k": [
    #     {"food_name": "pizza",        "display_name": "Pizza",        "confidence": 0.9342},
    #     {"food_name": "focaccia",     "display_name": "Focaccia",     "confidence": 0.0412},
    #     {"food_name": "garlic_bread", "display_name": "Garlic Bread", "confidence": 0.0131},
    #   ]
    # }

IMPORTANT: Instantiate this class ONCE and reuse it. Loading a model
is expensive; you do not want to do it per request.
"""

import logging
import os
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# The 101 Food-101 class names in alphabetical order.
# This MUST match the order used when training (torchvision ImageFolder sorts alphabetically).
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
    """Convert Food-101 class name to human-readable display name.
    Example: 'apple_pie' -> 'Apple Pie'
    """
    return class_name.replace("_", " ").title()


def _download_model(model_path: Path) -> bool:
    """
    Download the model file from MODEL_DOWNLOAD_URL if set in the environment.
    Returns True on success, False otherwise.
    """
    url = os.environ.get("MODEL_DOWNLOAD_URL", "").strip()
    if not url:
        return False

    try:
        import urllib.request
        model_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Downloading model from %s ...", url)
        urllib.request.urlretrieve(url, model_path)
        logger.info("Model downloaded successfully to %s", model_path)
        return True
    except Exception as exc:
        logger.error("Failed to download model: %s", exc)
        if model_path.exists():
            model_path.unlink()
        return False


def _build_food101_model() -> "torch.nn.Module":
    """
    Build EfficientNetB0 with 101 output classes using timm.

    Returns a model with random classification head weights.
    Call .load_state_dict() after this to load trained weights.
    """
    import timm
    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=101,
    )
    return model


class Predictor:
    """
    Wraps the trained PyTorch model and provides a clean predict() interface.

    Model loading is lazy -- the model is loaded on the first call to predict()
    so importing this class does not incur loading overhead.
    """

    def __init__(
        self,
        model_path: Union[str, Path, None] = None,
        top_k: int = 3,
    ) -> None:
        """
        Parameters
        ----------
        model_path : str | Path | None
            Path to the trained .pt model weights file.
            Defaults to MODEL_PATH from the environment, or 'ml/models/food101_v1.pt'.
        top_k : int
            Number of top predictions to return. Default: 3.
        """
        if model_path is None:
            model_path = os.environ.get("MODEL_PATH", "ml/models/food101_v1.pt")
        self.model_path = Path(model_path)
        self.top_k = top_k
        self._model = None       # Lazy loaded
        self._device = None      # Set on load

    def _load_model(self) -> None:
        """
        Load the PyTorch model weights from disk.

        If the weights file is missing and MODEL_DOWNLOAD_URL is set,
        the file is downloaded automatically.

        Falls back to ImageNet pretrained weights from timm if no
        Food-101 weights file exists (for development/testing only).

        Raises
        ------
        RuntimeError
            If timm is not installed or the model fails to build.
        """
        import torch
        import timm

        self._device = torch.device("cpu")  # CPU only for now

        if self.model_path.exists():
            # Load trained Food-101 weights
            logger.info("Loading Food-101 model weights from %s ...", self.model_path)
            model = _build_food101_model()
            state_dict = torch.load(self.model_path, map_location=self._device, weights_only=True)
            model.load_state_dict(state_dict)
            model.eval()
            self._model = model
            logger.info("Food-101 model loaded successfully.")
        else:
            # Try downloading
            logger.info("Model weights not found at %s. Attempting download...", self.model_path)
            downloaded = _download_model(self.model_path)

            if downloaded and self.model_path.exists():
                self._load_model()  # Retry after download
                return

            # Fallback: ImageNet pretrained weights from timm (development placeholder)
            logger.warning(
                "No Food-101 weights available. Using ImageNet pretrained weights from timm "
                "(predictions will NOT be food-specific). "
                "Run scripts/download_model.py or set MODEL_DOWNLOAD_URL to fix this."
            )
            model = timm.create_model(
                "efficientnet_b0",
                pretrained=True,    # Downloads ImageNet weights from timm hub
                num_classes=101,    # Replace the final layer for 101 classes
            )
            model.eval()
            self._model = model

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
            - food_name    : str   -- Top-1 class name (e.g. 'pizza')
            - display_name : str   -- Human-readable name (e.g. 'Pizza')
            - confidence   : float -- Top-1 confidence score (0.0-1.0)
            - top_k        : list  -- Top-K predictions, each with:
                             { food_name, display_name, confidence }

        Raises
        ------
        FileNotFoundError
            If a file path is given but the file does not exist.
        RuntimeError
            If the model fails to make a prediction.
        """
        import torch
        torch.set_num_threads(1)  # Force 1 thread to prevent memory spikes on small servers

        # Load model on first call
        if self._model is None:
            self._load_model()

        # Preprocess the image -> shape (1, 3, 224, 224)
        from ml.preprocessing.image_preprocessor import preprocess_image
        tensor = preprocess_image(image_source).to(self._device)

        # Run inference
        try:
            with torch.no_grad():
                logits = self._model(tensor)      # shape: (1, 101)
                probs = torch.softmax(logits, dim=1)[0]  # shape: (101,)
        except Exception as exc:
            raise RuntimeError(f"Model inference failed: {exc}") from exc

        # Get top-K predictions
        top_k = min(self.top_k, len(FOOD_CLASSES))
        top_probs, top_indices = torch.topk(probs, top_k)

        top_k_results = []
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
            food_name = FOOD_CLASSES[idx]
            top_k_results.append({
                "food_name": food_name,
                "display_name": _class_name_to_display(food_name),
                "confidence": float(prob),
            })
        
        try:
            best = top_k_results[0]
            return {
                "food_name": best["food_name"],
                "display_name": best["display_name"],
                "confidence": best["confidence"],
                "top_k": top_k_results,
            }
        finally:
            import gc
            gc.collect()
