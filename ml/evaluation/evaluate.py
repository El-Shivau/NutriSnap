"""
Model Evaluation Script
========================

Evaluates a trained NutriSnap model against the Food-101 test set.

Outputs
-------
- Overall accuracy and loss
- Top-5 accuracy
- Per-class precision, recall, F1 score (classification report)
- Confusion matrix (saved as a heatmap image)
- Training history plots (accuracy and loss curves)

Usage
-----
    python ml/evaluation/evaluate.py --model ml/models/food101_v1.keras

Implementation is deferred to Phase 3.
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained NutriSnap model.")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to the trained .keras model file.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/dataset/food-101",
        help="Path to the Food-101 dataset root.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/evaluation/reports",
        help="Directory where evaluation outputs are saved.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main evaluation entry point. Implemented in Phase 3.
    """
    args = parse_args()

    logger.info("Evaluating model : %s", args.model)
    logger.info("Data directory   : %s", args.data_dir)
    logger.info("Output directory : %s", args.output_dir)

    # TODO: Implement in Phase 3:
    # 1. Load the test dataset.
    # 2. Load the model with keras.models.load_model().
    # 3. model.evaluate() → overall accuracy, loss.
    # 4. model.predict() on test set → generate confusion matrix.
    # 5. sklearn.metrics.classification_report() → per-class metrics.
    # 6. Save confusion matrix heatmap using seaborn.
    # 7. Save training history plots (if history JSON is available).
    raise NotImplementedError("Evaluation pipeline implemented in Phase 3.")


if __name__ == "__main__":
    main()
