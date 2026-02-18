from extensions import db


class NutritionInfo(db.Model):
    __tablename__ = 'nutrition_info'

    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    calories_per_100g = db.Column(db.Float, default=0)
    protein_per_100g = db.Column(db.Float, default=0)
    carbs_per_100g = db.Column(db.Float, default=0)
    fat_per_100g = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<NutritionInfo {self.food_name}>'

    def to_dict(self):
        return {
            'food_name': self.food_name,
            'calories_per_100g': self.calories_per_100g,
            'protein_per_100g': self.protein_per_100g,
            'carbs_per_100g': self.carbs_per_100g,
            'fat_per_100g': self.fat_per_100g
        }
