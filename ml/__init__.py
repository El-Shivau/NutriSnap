"""
ML Package
==========

This package is completely independent of Flask.

All machine learning code lives here:
  - preprocessing/  : Image preprocessing utilities
  - training/       : Training pipeline (EfficientNetB0)
  - inference/      : Prediction module (loaded by the Flask backend)
  - evaluation/     : Evaluation scripts and metrics
  - models/         : Saved .keras model files
  - dataset/        : Dataset download instructions

IMPORTANT: Never import Flask in this package.
"""
