#!/usr/bin/env bash
# =============================================================================
# NutriSnap – Database Initialisation Script
# =============================================================================
# Creates all database tables and seeds the nutrition database.
# Usage:  bash scripts/init_db.sh
# Run from the project root directory.
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate virtual environment if present
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Load environment variables from .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "============================================"
echo "  NutriSnap – Database Initialisation"
echo "============================================"

# --- 1. Create all tables ---------------------------------------------------
echo ""
echo "[1/2] Creating database tables..."
python3 - <<'EOF'
from backend.app import create_app
from backend.extensions import db
import backend.models  # Import all models to register them

app = create_app("development")
with app.app_context():
    db.create_all()
    print("      All tables created successfully.")
EOF

# --- 2. Seed nutrition data -------------------------------------------------
echo ""
echo "[2/2] Seeding nutrition database..."
python3 data/seeds/seed_nutrition.py

echo ""
echo "============================================"
echo "  ✅ Database initialisation complete!"
echo "============================================"
echo ""
