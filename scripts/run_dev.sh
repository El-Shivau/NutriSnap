#!/usr/bin/env bash
# =============================================================================
# NutriSnap – Development Server Script
# =============================================================================
# Usage:  bash scripts/run_dev.sh
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
echo "  NutriSnap – Development Server"
echo "============================================"
echo "  URL : http://127.0.0.1:5000"
echo "  Mode: ${FLASK_ENV:-development}"
echo "============================================"
echo ""

# Run Flask development server
flask --app backend.wsgi run --debug --host=127.0.0.1 --port=5000
