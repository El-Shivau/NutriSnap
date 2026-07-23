# NutriSnap – Model Training Guide

> Full implementation of this pipeline is in **Phase 3**. This document describes the complete training process end-to-end.

## Overview

We train **EfficientNetB0** on the **Food-101** dataset using **transfer learning** in two phases.

---

## Step 1: Download the Dataset

See [`ml/dataset/README.md`](../ml/dataset/README.md) for download instructions.

Expected structure after extraction:
```
ml/dataset/food-101/images/apple_pie/  ...  (101 folders)
ml/dataset/food-101/meta/train.txt
ml/dataset/food-101/meta/test.txt
```

---

## Step 2: Configure Training

Edit `ml/training/config.py` to adjust hyperparameters:
- `PHASE1_EPOCHS`, `PHASE2_EPOCHS`
- `PHASE1_LEARNING_RATE`, `PHASE2_LEARNING_RATE`
- `PHASE1_BATCH_SIZE`

---

## Step 3: Run Training

```bash
# Activate virtual environment
source venv/bin/activate

# Install dev dependencies (includes TensorFlow, matplotlib etc.)
pip install -r requirements-dev.txt

# Run Phase 3 training pipeline
python ml/training/train.py --version v1 --data-dir ml/dataset/food-101
```

Expected training time:
- GPU (RTX 3080): ~2–4 hours total
- CPU only: 24–48 hours (not recommended)

---

## Step 4: Evaluate the Model

```bash
python ml/evaluation/evaluate.py \
  --model ml/models/food101_v1.keras \
  --data-dir ml/dataset/food-101 \
  --output-dir ml/evaluation/reports
```

Outputs:
- `food101_v1_accuracy.json` — top-1 and top-5 accuracy
- `food101_v1_confusion_matrix.png` — 101×101 heatmap
- `food101_v1_classification_report.txt` — per-class precision/recall/F1

---

## Two-Phase Transfer Learning Strategy

### Phase 1 — Head Only (Frozen Base)

```
EfficientNetB0 (imagenet weights, FROZEN)
    ↓
GlobalAveragePooling2D
    ↓
Dropout(0.3)
    ↓
Dense(101, activation='softmax')
```

- Trains ONLY the new classification head.
- Base model weights do NOT change.
- Goal: quickly adapt the head to Food-101 classes.
- Typical result: ~60–70% top-1 accuracy.

### Phase 2 — Fine-tuning (Unfreeze Top Layers)

- Unfreeze EfficientNetB0 layers from `FINE_TUNE_AT_LAYER` onwards.
- Use a much smaller learning rate (10× smaller than Phase 1).
- Goal: adapt EfficientNet features to food-specific patterns.
- Expected result: ~75–85% top-1 accuracy.

---

## Expected Results on Food-101

| Metric | Expected Value |
|--------|---------------|
| Top-1 Accuracy | ~75–85% |
| Top-5 Accuracy | ~92–96% |
| Training time (GPU) | ~2–4 hours |

Note: Original Food-101 paper reports 50.76% with GoogLeNet.
EfficientNetB0 with fine-tuning should significantly exceed this.
