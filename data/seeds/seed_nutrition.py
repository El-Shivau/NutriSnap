"""
Database Seeder — Nutrition Data
==================================

Loads the nutrition_data.json file into the database's nutrition table.

This script is idempotent — running it multiple times will NOT create
duplicate records. If a food_name already exists, it is updated.

Usage
-----
Run from the project root directory after the Flask app and DB are
initialised:

    python data/seeds/seed_nutrition.py

Or via the shell script:

    bash scripts/init_db.sh

Requirements
------------
- The Flask app must be importable (run from project root).
- The database must already be created (flask db upgrade, or create_all()).
- data/nutrition/nutrition_data.json must exist.
"""

import json
import logging
import os
import sys

# Allow imports from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def seed_nutrition() -> None:
    """
    Read nutrition_data.json and upsert all records into the nutrition table.

    Uses an INSERT OR REPLACE strategy so the script is safe to re-run.
    """
    from backend.app import create_app
    from backend.extensions import db
    from backend.models.nutrition import Nutrition

    # Create the Flask app in development mode
    app = create_app("development")

    # Resolve path to the JSON file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(project_root, "data", "nutrition", "nutrition_data.json")

    if not os.path.exists(json_path):
        logger.error("nutrition_data.json not found at: %s", json_path)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    foods = data.get("foods", [])
    logger.info("Loaded %d food entries from nutrition_data.json", len(foods))

    inserted = 0
    updated = 0

    with app.app_context():
        # Ensure the table exists
        db.create_all()

        for entry in foods:
            # Check if this food already exists
            existing = Nutrition.query.filter_by(food_name=entry["food_name"]).first()

            if existing:
                # Update existing record
                existing.display_name = entry["display_name"]
                existing.calories = entry["calories"]
                existing.protein_g = entry["protein_g"]
                existing.fat_g = entry["fat_g"]
                existing.carbs_g = entry["carbs_g"]
                existing.fiber_g = entry["fiber_g"]
                existing.serving_size_g = entry["serving_size_g"]
                updated += 1
            else:
                # Insert new record
                nutrition = Nutrition(
                    food_name=entry["food_name"],
                    display_name=entry["display_name"],
                    calories=entry["calories"],
                    protein_g=entry["protein_g"],
                    fat_g=entry["fat_g"],
                    carbs_g=entry["carbs_g"],
                    fiber_g=entry["fiber_g"],
                    serving_size_g=entry["serving_size_g"],
                )
                db.session.add(nutrition)
                inserted += 1

        db.session.commit()

    logger.info("✅ Seeding complete — %d inserted, %d updated", inserted, updated)


if __name__ == "__main__":
    seed_nutrition()
