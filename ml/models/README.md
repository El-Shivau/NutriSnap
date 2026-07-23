# Trained Model Files

## Naming Convention

All model files must follow this versioning format:

```
food101_v1.keras
food101_v2.keras
food101_v3.keras
```

**Never use** `best_model.h5` or generic names. Every version must be traceable.

## Version Log

| Version | Date | Top-1 Accuracy | Top-5 Accuracy | Notes |
|---------|------|---------------|---------------|-------|
| v1 | TBD | TBD | TBD | Initial training — Phase 3 |
| v2 | TBD | TBD | TBD | Fine-tuned — Phase 3 |

## Corresponding Metrics

Each model version **must** have corresponding evaluation files in `ml/evaluation/reports/`:

```
ml/evaluation/reports/
├── food101_v1_accuracy.json
├── food101_v1_confusion_matrix.png
├── food101_v1_classification_report.txt
└── food101_v1_training_history.json
```

## Why .gitignore Excludes Model Files

Model files are large binary files (50–200 MB) that should NOT be committed to git.
Instead, store them in:
- A shared cloud drive (Google Drive, S3, etc.)
- A model registry (MLflow, DVC, Weights & Biases)

Document the download URL here after training is complete.

## Loading the Model in Production

```python
from ml.inference.predictor import Predictor

# Load once at app startup — NOT per request
predictor = Predictor(model_path="ml/models/food101_v1.keras")

# Use in each request
result = predictor.predict("path/to/image.jpg")
```
