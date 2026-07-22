"""
Training Script — EfficientNetB0 on Food-101
=============================================

This script trains a food recognition model using EfficientNetB0
as the base (transfer learning) and a custom classification head.

Training Strategy (Two-Phase)
-------------------------------
Phase 1 — HEAD ONLY training:
    - EfficientNetB0 base layers are FROZEN.
    - Only the new classification head is trained.
    - Runs for PHASE1_EPOCHS with a higher learning rate.
    - Goal: quickly fit the classification head.

Phase 2 — FINE-TUNING:
    - The top layers of EfficientNetB0 are UNFROZEN.
    - The entire model is trained end-to-end.
    - Uses a much smaller learning rate to avoid destroying pretrained weights.
    - Goal: adapt EfficientNet features to food-specific patterns.

Usage
-----
    python ml/training/train.py --version v1
    python ml/training/train.py --version v2 --epochs-phase1 15 --epochs-phase2 10

Outputs
-------
    ml/models/food101_v1.keras    ← Best model weights
    ml/training/checkpoints/      ← Per-epoch checkpoints
    ml/evaluation/reports/        ← Accuracy, loss, confusion matrix

IMPORTANT: Run this script from the project root directory.
"""

import argparse
import logging
import os
import sys

# Add project root to sys.path so we can import ml modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.training.config import (
    AUGMENTATION_CONFIG,
    BATCH_SIZE_PHASE1,
    CHECKPOINT_DIR,
    EARLY_STOPPING_PATIENCE,
    EVALUATION_OUTPUT_DIR,
    FINE_TUNE_AT_LAYER,
    IMAGE_SIZE,
    MIN_LEARNING_RATE,
    MODEL_OUTPUT_PATH,
    NUM_CLASSES,
    PHASE1_EPOCHS,
    PHASE1_LEARNING_RATE,
    PHASE2_EPOCHS,
    PHASE2_LEARNING_RATE,
    REDUCE_LR_FACTOR,
    REDUCE_LR_PATIENCE,
    VALIDATION_SPLIT,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the training script."""
    parser = argparse.ArgumentParser(
        description="Train EfficientNetB0 on the Food-101 dataset.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/dataset/food-101",
        help="Path to the Food-101 dataset root directory.",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1",
        help="Model version string (e.g. v1, v2). Used in the output filename.",
    )
    parser.add_argument(
        "--epochs-phase1",
        type=int,
        default=PHASE1_EPOCHS,
        help="Number of training epochs for Phase 1 (head-only).",
    )
    parser.add_argument(
        "--epochs-phase2",
        type=int,
        default=PHASE2_EPOCHS,
        help="Number of training epochs for Phase 2 (fine-tuning).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for both training phases.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main training entry point.

    Implementation is deferred to Phase 3.
    This stub establishes the argument interface and logging setup.
    """
    args = parse_args()

    logger.info("=" * 60)
    logger.info("NutriSnap — EfficientNetB0 Training Pipeline")
    logger.info("=" * 60)
    logger.info("Data directory : %s", args.data_dir)
    logger.info("Model version  : %s", args.version)
    logger.info("Phase 1 epochs : %d", args.epochs_phase1)
    logger.info("Phase 2 epochs : %d", args.epochs_phase2)
    logger.info("Batch size     : %d", args.batch_size)
    logger.info("=" * 60)

    # TODO: Implement in Phase 3:
    # 1. Load and split the Food-101 dataset.
    # 2. Create ImageDataGenerators with augmentation for training.
    # 3. Build EfficientNetB0 base model (weights='imagenet', include_top=False).
    # 4. Add GlobalAveragePooling2D, Dropout, Dense(101, softmax) head.
    # 5. Phase 1: Freeze base, compile with high LR, train for phase1_epochs.
    # 6. Phase 2: Unfreeze top layers, compile with low LR, train for phase2_epochs.
    # 7. Save best model to ml/models/food101_{version}.keras.
    # 8. Save training history, generate plots.
    raise NotImplementedError("Training pipeline will be implemented in Phase 3.")


if __name__ == "__main__":
    main()
