"""
Nutrition Model
===============

Stores the nutritional information for each food class in the Food-101 dataset.

Table: nutrition
----------------
- id              : Primary key (auto-incremented integer).
- food_name       : Unique name matching the Food-101 class label (e.g. "pizza").
- display_name    : Human-readable name (e.g. "Pizza").
- calories        : Kilocalories per standard serving.
- protein_g       : Protein in grams per serving.
- fat_g           : Total fat in grams per serving.
- carbs_g         : Total carbohydrates in grams per serving.
- fiber_g         : Dietary fibre in grams per serving.
- serving_size_g  : Standard serving size in grams.
- notes           : Optional notes (e.g. "values are for a typical slice").

Design Decisions
----------------
- food_name is lowercase with underscores to match Food-101 folder names.
- Values represent a standard single serving (not 100 g).
- This table is populated via data/seeds/seed_nutrition.py, not hardcoded.
- All nutritional values are approximate (USDA / standard reference averages).
"""

from backend.extensions import db


class Nutrition(db.Model):
    """SQLAlchemy model for the nutritional database."""

    __tablename__ = "nutrition"

    # Primary key
    id: int = db.Column(db.Integer, primary_key=True)

    # Food identity
    food_name: str = db.Column(db.String(100), unique=True, nullable=False, index=True)
    display_name: str = db.Column(db.String(100), nullable=False)

    # Nutritional values per serving
    calories: float = db.Column(db.Float, nullable=False)
    protein_g: float = db.Column(db.Float, nullable=False)
    fat_g: float = db.Column(db.Float, nullable=False)
    carbs_g: float = db.Column(db.Float, nullable=False)
    fiber_g: float = db.Column(db.Float, nullable=False)

    # Serving information
    serving_size_g: float = db.Column(db.Float, nullable=False)

    # Optional notes
    notes: str | None = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Nutrition food={self.food_name!r} calories={self.calories}>"

    def to_dict(self) -> dict:
        """Serialise nutritional data to a dictionary."""
        return {
            "food_name": self.food_name,
            "display_name": self.display_name,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "fat_g": self.fat_g,
            "carbs_g": self.carbs_g,
            "fiber_g": self.fiber_g,
            "serving_size_g": self.serving_size_g,
            "notes": self.notes,
        }
