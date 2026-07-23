"""
Training Configuration
=======================

All hyperparameters for EfficientNetB0 training are defined here.
Centralising them makes it easy to experiment — change values here
rather than hunting through the training script.

These values are the recommended starting points.
Phase 3 will tune them based on validation metrics.
"""

# -------------------------------------------------------------------------
# Model
# -------------------------------------------------------------------------
BASE_MODEL_NAME: str = "EfficientNetB0"  # From tf.keras.applications

# -------------------------------------------------------------------------
# Image
# -------------------------------------------------------------------------
IMAGE_SIZE: tuple[int, int] = (224, 224)  # EfficientNetB0 input resolution
IMAGE_CHANNELS: int = 3                   # RGB

# -------------------------------------------------------------------------
# Dataset
# -------------------------------------------------------------------------
NUM_CLASSES: int = 101           # Food-101 has exactly 101 classes
VALIDATION_SPLIT: float = 0.2   # 20% of training data used for validation

# -------------------------------------------------------------------------
# Training — Phase 1: Train only the classification head
# (base model layers are frozen)
# -------------------------------------------------------------------------
PHASE1_EPOCHS: int = 10
PHASE1_LEARNING_RATE: float = 1e-3
PHASE1_BATCH_SIZE: int = 32

# -------------------------------------------------------------------------
# Training — Phase 2: Fine-tune upper layers of EfficientNetB0
# (unfreeze the top N layers of the base model)
# -------------------------------------------------------------------------
PHASE2_EPOCHS: int = 10
PHASE2_LEARNING_RATE: float = 1e-4   # Lower LR for fine-tuning
PHASE2_BATCH_SIZE: int = 32
FINE_TUNE_AT_LAYER: int = 100        # Unfreeze layers from this index onwards

# -------------------------------------------------------------------------
# Data Augmentation (applied to training data only)
# -------------------------------------------------------------------------
AUGMENTATION_CONFIG: dict = {
    "rotation_range": 20,        # Degrees of random rotation
    "width_shift_range": 0.2,
    "height_shift_range": 0.2,
    "shear_range": 0.2,
    "zoom_range": 0.2,
    "horizontal_flip": True,
    "fill_mode": "nearest",
}

# -------------------------------------------------------------------------
# Model Checkpointing
# -------------------------------------------------------------------------
CHECKPOINT_DIR: str = "ml/training/checkpoints"

# Model output versioning — increment on each successful training run
MODEL_VERSION: str = "v1"
MODEL_OUTPUT_PATH: str = f"ml/models/food101_{MODEL_VERSION}.keras"

# -------------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------------
EARLY_STOPPING_PATIENCE: int = 5   # Stop training after N epochs of no improvement
REDUCE_LR_PATIENCE: int = 3        # Reduce LR after N epochs of no improvement
REDUCE_LR_FACTOR: float = 0.5      # Multiply LR by this factor when reducing
MIN_LEARNING_RATE: float = 1e-7    # Never reduce below this value

# -------------------------------------------------------------------------
# Evaluation
# -------------------------------------------------------------------------
EVALUATION_OUTPUT_DIR: str = "ml/evaluation/reports"
TOP_K_ACCURACY: int = 5            # Also compute top-5 accuracy metric
