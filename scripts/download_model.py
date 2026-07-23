#!/usr/bin/env python3
"""
Model Download Script
======================

Downloads the pre-trained Food-101 EfficientNetB0 model from the
URL specified in MODEL_DOWNLOAD_URL (environment variable or .env file).

Usage
-----
    # Standard usage (reads MODEL_DOWNLOAD_URL from .env)
    python scripts/download_model.py

    # Override the URL directly
    MODEL_DOWNLOAD_URL=https://... python scripts/download_model.py

Where to get MODEL_DOWNLOAD_URL
--------------------------------
After training the model on Google Colab (see notebooks/train_food101_colab.ipynb):
  1. Upload the .pt file to a GitHub Release:
     GitHub repo -> Releases -> Draft a new release -> Attach binary files
     The URL will look like:
     https://github.com/YOUR_USERNAME/NutriSnap/releases/download/v1.0/food101_v1.pt

  2. Set this URL in your .env file:
     MODEL_DOWNLOAD_URL=https://github.com/YOUR_USERNAME/NutriSnap/releases/download/v1.0/food101_v1.pt

  3. Set the same variable in your Render environment variables.

Render Build Command
---------------------
Add to Render -> Service -> Build Command:
    pip install -r requirements.txt && python scripts/download_model.py
"""

import os
import sys
import urllib.request
from pathlib import Path

# Allow running from any directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file manually (avoid importing dotenv here to keep deps minimal)
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    url = os.environ.get("MODEL_DOWNLOAD_URL", "").strip()
    model_path_str = os.environ.get("MODEL_PATH", "ml/models/food101_v1.pt").strip()
    model_path = PROJECT_ROOT / model_path_str

    if not url:
        print("=" * 60)
        print("  ERROR: MODEL_DOWNLOAD_URL is not set.")
        print("=" * 60)
        print()
        print("  Add this to your .env file:")
        print("  MODEL_DOWNLOAD_URL=https://github.com/YOUR_USERNAME/NutriSnap/")
        print("                     releases/download/v1.0/food101_v1.pt")
        print()
        print("  Steps to get the URL:")
        print("  1. Train on Google Colab using notebooks/train_food101_colab.ipynb")
        print("  2. Download the .pt file from Colab")
        print("  3. Upload it to a GitHub Release in your NutriSnap repository")
        print("  4. Copy the download URL and set MODEL_DOWNLOAD_URL in .env")
        print()
        sys.exit(1)

    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  Model already exists at {model_path} ({size_mb:.1f} MB). Skipping download.")
        sys.exit(0)

    print("=" * 60)
    print("  NutriSnap — Model Download")
    print("=" * 60)
    print(f"  URL        : {url}")
    print(f"  Destination: {model_path}")
    print()

    model_path.parent.mkdir(parents=True, exist_ok=True)

    def _report_progress(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            pct = min(100, downloaded * 100 // total_size)
            mb_done = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  Downloading... {pct}% ({mb_done:.1f} / {mb_total:.1f} MB)", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, model_path, reporthook=_report_progress)
        print()  # newline after progress
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"\n  Model downloaded successfully! ({size_mb:.1f} MB)")
        print(f"  Saved to: {model_path}")
        print("=" * 60)
    except Exception as exc:
        print(f"\n  ERROR: Download failed: {exc}")
        if model_path.exists():
            model_path.unlink()  # Remove partial download
        sys.exit(1)


if __name__ == "__main__":
    main()
