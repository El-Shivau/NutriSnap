#!/usr/bin/env bash
# =============================================================================
# NutriSnap – Environment Setup Script
# =============================================================================
# Usage:  bash scripts/setup_env.sh
# Run from the project root directory.
# =============================================================================

set -e  # Exit immediately on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================"
echo "  NutriSnap – Environment Setup"
echo "============================================"

# --- 1. Check Python version ------------------------------------------------
echo ""
echo "[1/5] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "      Found: $PYTHON_VERSION"

# --- 2. Create virtual environment ------------------------------------------
echo ""
echo "[2/5] Creating virtual environment (venv/)..."
if [ -d "venv" ]; then
    echo "      venv/ already exists — skipping creation."
else
    python3 -m venv venv
    echo "      Virtual environment created."
fi

# --- 3. Activate and install dependencies -----------------------------------
echo ""
echo "[3/5] Installing dependencies..."
source venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "      Production dependencies installed."
echo ""
read -p "      Install development dependencies too? [y/N] " install_dev
if [[ "$install_dev" =~ ^[Yy]$ ]]; then
    pip install -r requirements-dev.txt --quiet
    echo "      Development dependencies installed."
fi

# --- 4. Set up .env file ----------------------------------------------------
echo ""
echo "[4/5] Setting up .env file..."
if [ -f ".env" ]; then
    echo "      .env already exists — skipping."
else
    cp .env.example .env
    echo "      Created .env from .env.example."
    echo "      ⚠️  IMPORTANT: Edit .env and set FLASK_SECRET_KEY before running."
fi

# --- 5. Create required directories -----------------------------------------
echo ""
echo "[5/5] Creating required directories..."
mkdir -p logs
mkdir -p backend/uploads
mkdir -p ml/models
mkdir -p ml/training/checkpoints
mkdir -p ml/evaluation/reports

echo "      Directories created."

# --- Done -------------------------------------------------------------------
echo ""
echo "============================================"
echo "  ✅ Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and set a strong FLASK_SECRET_KEY"
echo "  2. Run:  bash scripts/init_db.sh"
echo "  3. Run:  bash scripts/run_dev.sh"
echo ""
