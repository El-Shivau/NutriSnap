"""
Image Preprocessing Module
===========================

This module provides image preprocessing utilities for the NutriSnap
food recognition pipeline using PyTorch + torchvision.

It is used in TWO places:
  1. During training   : ml/training/train.py
  2. During inference  : ml/inference/predictor.py

Having a single shared preprocessing module is critical -- the EXACT
same transformations applied during training MUST be applied at
inference time. Any mismatch will cause the model to produce
incorrect predictions.

EfficientNetB0 (timm) Input Requirements
-----------------------------------------
- Image size  : 224 x 224 pixels
- Pixel range : [0.0, 1.0] float32
- Normalisation: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
  (ImageNet statistics used by all timm models)
- Channel order: RGB
"""

import io
import logging
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# EfficientNetB0 (timm default) expects 224x224 images
TARGET_SIZE: tuple[int, int] = (224, 224)

# ImageNet normalisation constants (used by all timm pretrained models)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


def load_image(image_source: Union[str, Path, bytes]) -> Image.Image:
    """
    Load an image from a file path or raw bytes.

    Parameters
    ----------
    image_source : str | Path | bytes
        Either a file path (string or Path object) or raw image bytes
        (e.g. from an HTTP multipart upload).

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
    try:
        if isinstance(image_source, bytes):
            image = Image.open(io.BytesIO(image_source))
        else:
            path = Path(image_source)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            image = Image.open(path)

        return image.convert("RGB")

    except FileNotFoundError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to load image: {exc}") from exc


def resize_image(image: Image.Image, size: tuple[int, int] = TARGET_SIZE) -> Image.Image:
    """
    Resize an image to the target dimensions using LANCZOS resampling.

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
    return image.resize(size, Image.LANCZOS)


def image_to_array(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a NumPy array.

    The output shape is (224, 224, 3) -- height x width x channels.
    Pixel values are in the range [0, 255] as uint8.

    Parameters
    ----------
    image : PIL.Image.Image
        The resized RGB image.

    Returns
    -------
    np.ndarray
        Array of shape (224, 224, 3) with dtype uint8.
    """
    return np.array(image, dtype=np.uint8)


def preprocess_image(
    image_source: Union[str, Path, bytes],
    target_size: tuple[int, int] = TARGET_SIZE,
) -> "torch.Tensor":
    """
    Full preprocessing pipeline for a single image.

    Steps:
    1. Load the image (from path or bytes).
    2. Convert to RGB.
    3. Resize to target_size using LANCZOS.
    4. Normalise to [0, 1] float32.
    5. Apply ImageNet mean/std normalisation.
    6. Add batch dimension -> shape (1, 3, H, W).

    Parameters
    ----------
    image_source : str | Path | bytes
        File path or raw bytes of the image to preprocess.
    target_size : tuple[int, int]
        Target image dimensions. Default: (224, 224).

    Returns
    -------
    torch.Tensor
        Preprocessed tensor of shape (1, 3, 224, 224), ready for
        model.forward().

    Example
    -------
    >>> tensor = preprocess_image("images/pizza.jpg")
    >>> tensor.shape
    torch.Size([1, 3, 224, 224])
    """
    import torch
    from torchvision import transforms

    transform = transforms.Compose([
        transforms.Resize(target_size, interpolation=transforms.InterpolationMode.LANCZOS),
        transforms.ToTensor(),                          # [0,255] uint8 -> [0.0,1.0] float32, HWC->CHW
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    image = load_image(image_source)
    tensor = transform(image)          # shape: (3, H, W)
    return tensor.unsqueeze(0)         # shape: (1, 3, H, W)
