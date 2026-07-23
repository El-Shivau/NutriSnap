"""
FoodLog Model
=============

Records a user's food consumption event.

Each time a user uploads an image, confirms the prediction, and saves
the entry, one FoodLog row is created. This enables the history and
dashboard features.

Table: food_logs
----------------
- id              : Primary key (auto-incremented integer).
- user_id         : Foreign key → users.id (required).
- food_name       : Recognised food name (e.g. "pizza").
- display_name    : Human-readable name (e.g. "Pizza").
- confidence      : Model confidence score for this prediction (0.0–1.0).
- calories        : Calories at time of logging (snapshot, not live lookup).
- protein_g       : Protein in grams.
- fat_g           : Fat in grams.
- carbs_g         : Carbohydrates in grams.
- fiber_g         : Dietary fibre in grams.
- serving_size_g  : Serving size in grams.
- image_filename  : Filename of the uploaded image (stored in uploads/).
- logged_at       : UTC timestamp of when the log entry was created.
- notes           : Optional user notes for this log entry.

Design Decision: Nutrition Snapshot
------------------------------------
Nutritional values are copied from the Nutrition table at the time of
logging (rather than referencing via FK). This ensures that if the
Nutrition table is updated later, historical log entries remain accurate.
"""

from datetime import datetime, timezone

from backend.extensions import db


class FoodLog(db.Model):
    """SQLAlchemy model representing a single food consumption log entry."""

    __tablename__ = "food_logs"

    # Primary key
    id: int = db.Column(db.Integer, primary_key=True)

    # Foreign key — every log must belong to a user
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Food identity
    food_name: str = db.Column(db.String(100), nullable=False)
    display_name: str = db.Column(db.String(100), nullable=False)

    # Model prediction confidence (0.0 to 1.0)
    confidence: float = db.Column(db.Float, nullable=False)

    # Nutritional snapshot (copied from Nutrition table at log time)
    calories: float = db.Column(db.Float, nullable=False)
    protein_g: float = db.Column(db.Float, nullable=False)
    fat_g: float = db.Column(db.Float, nullable=False)
    carbs_g: float = db.Column(db.Float, nullable=False)
    fiber_g: float = db.Column(db.Float, nullable=False)
    serving_size_g: float = db.Column(db.Float, nullable=False)

    # Image reference
    image_filename: str | None = db.Column(db.String(255), nullable=True)

    # Timestamp
    logged_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Optional user notes
    notes: str | None = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<FoodLog id={self.id} user_id={self.user_id} food={self.food_name!r}>"

    def to_dict(self) -> dict:
        """Serialise the food log entry to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "food_name": self.food_name,
            "display_name": self.display_name,
            "confidence": round(self.confidence * 100, 2),  # Convert to percentage
            "calories": self.calories,
            "protein_g": self.protein_g,
            "fat_g": self.fat_g,
            "carbs_g": self.carbs_g,
            "fiber_g": self.fiber_g,
            "serving_size_g": self.serving_size_g,
            "image_filename": self.image_filename,
            "logged_at": self.logged_at.isoformat(),
            "notes": self.notes,
        }
