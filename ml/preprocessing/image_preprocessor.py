"""
Image Preprocessing Module
===========================

This module provides image preprocessing utilities for the NutriSnap
food recognition pipeline.

It is used in TWO places:
  1. During training   : ml/training/train.py
  2. During inference  : ml/inference/predictor.py

Having a single shared preprocessing module is critical — the EXACT
same transformations applied during training MUST be applied at
inference time. Any mismatch will cause the model to produce
incorrect predictions.

EfficientNetB0 Input Requirements
----------------------------------
- Image size  : 224 × 224 pixels
- Pixel range : The raw [0, 255] uint8 values (EfficientNet includes
                its own internal rescaling via tf.keras.applications.efficientnet.preprocess_input)
- Channel order: RGB (Pillow and TensorFlow both use RGB by default)
"""

import logging
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# EfficientNetB0 expects 224×224 images
TARGET_SIZE: tuple[int, int] = (224, 224)


def load_image(image_source: Union[str, Path, bytes]) -> Image.Image:
    """
    Load an image from a file path or raw bytes.

    Parameters
    ----------
    image_source : str | Path | bytes
        Either a file path (string or Path object) or raw image bytes
        (e.g. from an HTTP request).

    Returns
    -------
    PIL.Image.Image
        The loaded image in RGB format.

    Raises
    ------
    FileNotFoundError
        If a file path is provided and the file does not exist.
    ValueError
        If the image cannot be opened or is not a valid image format.
    """
    # TODO: Implement in Phase 2
    # 1. If bytes → wrap in io.BytesIO and open with PIL.
    # 2. If path → verify it exists and open with PIL.
    # 3. Convert to RGB (handles RGBA, grayscale, etc.).
    raise NotImplementedError("load_image() — implemented in Phase 2")


def resize_image(image: Image.Image, size: tuple[int, int] = TARGET_SIZE) -> Image.Image:
    """
    Resize an image to the target dimensions using LANCZOS resampling.

    LANCZOS (also called Lanczos3) provides the best quality for
    downscaling and is preferred over simpler methods like BILINEAR.

    Parameters
    ----------
    image : PIL.Image.Image
        The input image (must be in RGB mode).
    size : tuple[int, int]
        Target (width, height) in pixels. Default is (224, 224).

    Returns
    -------
    PIL.Image.Image
        Resized image.
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("resize_image() — implemented in Phase 2")


def image_to_array(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a NumPy array.

    The output shape is (224, 224, 3) — height × width × channels.
    Pixel values are in the range [0, 255] as uint8.

    EfficientNet's preprocess_input() is applied separately in
    preprocess_image() to keep responsibilities single.

    Parameters
    ----------
    image : PIL.Image.Image
        The resized RGB image.

    Returns
    -------
    np.ndarray
        Array of shape (224, 224, 3) with dtype uint8.
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("image_to_array() — implemented in Phase 2")


def preprocess_image(
    image_source: Union[str, Path, bytes],
    target_size: tuple[int, int] = TARGET_SIZE,
) -> np.ndarray:
    """
    Full preprocessing pipeline for a single image.

    This is the main entry point used by both the training pipeline
    and the inference predictor. Steps:

    1. Load the image (from path or bytes).
    2. Convert to RGB.
    3. Resize to target_size.
    4. Convert to NumPy array (shape: H×W×3).
    5. Apply EfficientNet-specific normalisation.
    6. Add batch dimension (shape: 1×H×W×3).

    Parameters
    ----------
    image_source : str | Path | bytes
        File path or raw bytes of the image to preprocess.
    target_size : tuple[int, int]
        Target image dimensions. Default: (224, 224).

    Returns
    -------
    np.ndarray
        Preprocessed array of shape (1, 224, 224, 3), ready for
        model.predict().

    Example
    -------
    >>> tensor = preprocess_image("images/pizza.jpg")
    >>> tensor.shape
    (1, 224, 224, 3)
    """
    # TODO: Implement in Phase 2 using the helper functions above
    raise NotImplementedError("preprocess_image() — implemented in Phase 2")
