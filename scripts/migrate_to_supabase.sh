#!/usr/bin/env bash
# =============================================================================
# NutriSnap – Supabase Migration Script
# =============================================================================
# Creates all database tables in your Supabase PostgreSQL instance and
# seeds the 101-food nutrition database.
#
# Usage:  bash scripts/migrate_to_supabase.sh
# Run from the project root directory.
#
# Prerequisites:
#   1. Your DATABASE_URL in .env must point to Supabase
#      e.g. postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
#   2. Run: pip install -r requirements.txt  (includes psycopg2-binary)
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
echo "  NutriSnap – Supabase Migration"
echo "============================================"

# Safety check — confirm we are using a PostgreSQL URL
if [[ "$DATABASE_URL" != postgresql* ]]; then
    echo ""
    echo "  ❌ ERROR: DATABASE_URL in .env does not look like a PostgreSQL URI."
    echo "     Current value: ${DATABASE_URL:0:40}..."
    echo ""
    echo "  Set DATABASE_URL to your Supabase connection string first:"
    echo "  postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres"
    echo ""
    exit 1
fi

echo ""
echo "  Connecting to: ${DATABASE_URL:0:55}..."
echo ""

# --- 1. Create all tables ---------------------------------------------------
echo "[1/3] Creating all database tables in Supabase..."
python3 - <<'EOF'
import sys
from backend.app import create_app
from backend.extensions import db
import backend.models  # Registers all models including Friendship & LeaderboardEntry

app = create_app("production")
with app.app_context():
    db.create_all()
    print("      ✅ Tables created: users, food_logs, nutrition,")
    print("                        friendships, leaderboard_entries")
EOF

# --- 2. Seed nutrition database ---------------------------------------------
echo ""
echo "[2/3] Seeding nutrition database (101 foods)..."
python3 data/seeds/seed_nutrition.py

# --- 3. Verify ---------------------------------------------------------------
echo ""
echo "[3/3] Verifying tables exist..."
python3 - <<'EOF'
from backend.app import create_app
from backend.extensions import db
from sqlalchemy import inspect

app = create_app("production")
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    expected = {"users", "food_logs", "nutrition", "friendships", "leaderboard_entries"}
    found = set(tables)
    missing = expected - found

    if missing:
        print(f"      ⚠️  Missing tables: {missing}")
        raise SystemExit(1)
    else:
        for t in sorted(expected):
            print(f"      ✅ {t}")
EOF

echo ""
echo "============================================"
echo "  ✅ Supabase migration complete!"
echo "============================================"
echo ""
echo "  Next steps:"
echo "  1. Open your Supabase dashboard → Table Editor"
echo "  2. Confirm the tables above are visible"
echo "  3. Start the app: bash scripts/run_dev.sh"
echo ""
