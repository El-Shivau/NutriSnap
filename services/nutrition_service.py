import os
import csv
from models.nutrition_info import NutritionInfo
from extensions import db


class NutritionService:
    @staticmethod
    def seed_from_csv():
        """Populate the nutrition_info table from the CSV if empty."""
        existing = NutritionInfo.query.count()
        if existing > 0:
            print(f"Nutrition DB already has {existing} entries — skipping seed.")
            return

        csv_path = os.path.join(os.getcwd(), 'nutrition101.csv')
        if not os.path.exists(csv_path):
            print("WARNING: nutrition101.csv not found, cannot seed nutrition data.")
            return

        count = 0
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                name = row[1].strip().lower().replace('_', ' ')
                protein = float(row[2])
                fat = float(row[4])
                carbs = float(row[5])
                calories = round((protein * 4) + (carbs * 4) + (fat * 9), 2)

                entry = NutritionInfo(
                    food_name=name,
                    calories_per_100g=calories,
                    protein_per_100g=protein,
                    carbs_per_100g=carbs,
                    fat_per_100g=fat
                )
                db.session.add(entry)
                count += 1

        db.session.commit()
        print(f"Seeded {count} nutrition entries from CSV.")

    @staticmethod
    def lookup(food_name):
        """Find nutrition data by food name with fallback matching."""
        normalized = food_name.strip().lower().replace('_', ' ')

        # 1. Exact match
        entry = NutritionInfo.query.filter_by(food_name=normalized).first()
        if entry:
            return entry.to_dict()

        # 2. Partial match (LIKE)
        entry = NutritionInfo.query.filter(
            NutritionInfo.food_name.like(f'%{normalized}%')
        ).first()
        if entry:
            return entry.to_dict()

        return None
