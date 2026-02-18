from repositories.food_log_repository import FoodLogRepository


class RecommendationService:
    # Thresholds (daily averages)
    PROTEIN_LOW = 30  # grams
    CALORIE_HIGH = 2200  # kcal
    CARBS_HIGH = 250  # grams
    FAT_LOW = 20  # grams

    HEALTHY_MEALS = [
        # High protein
        {'meal_name': 'Grilled Chicken Breast', 'calories': 284, 'protein': 53, 'carbs': 0, 'fat': 6, 'tags': ['high_protein']},
        {'meal_name': 'Salmon Fillet', 'calories': 367, 'protein': 40, 'carbs': 0, 'fat': 22, 'tags': ['high_protein', 'healthy_fat']},
        {'meal_name': 'Egg White Omelette', 'calories': 150, 'protein': 26, 'carbs': 2, 'fat': 5, 'tags': ['high_protein', 'low_calorie']},
        {'meal_name': 'Greek Yogurt Bowl', 'calories': 180, 'protein': 20, 'carbs': 12, 'fat': 6, 'tags': ['high_protein']},
        {'meal_name': 'Lentil Soup', 'calories': 230, 'protein': 18, 'carbs': 40, 'fat': 1, 'tags': ['high_protein']},
        {'meal_name': 'Cottage Cheese & Berries', 'calories': 160, 'protein': 22, 'carbs': 10, 'fat': 3, 'tags': ['high_protein', 'low_calorie']},
        # Low calorie / lighter meals
        {'meal_name': 'Mixed Green Salad', 'calories': 120, 'protein': 5, 'carbs': 12, 'fat': 7, 'tags': ['low_calorie']},
        {'meal_name': 'Vegetable Stir-Fry', 'calories': 180, 'protein': 8, 'carbs': 20, 'fat': 8, 'tags': ['low_calorie']},
        {'meal_name': 'Miso Soup', 'calories': 84, 'protein': 6, 'carbs': 8, 'fat': 3, 'tags': ['low_calorie']},
        {'meal_name': 'Steamed Fish with Veggies', 'calories': 200, 'protein': 30, 'carbs': 8, 'fat': 5, 'tags': ['low_calorie', 'high_protein']},
        # Low carb
        {'meal_name': 'Zucchini Noodles with Pesto', 'calories': 220, 'protein': 6, 'carbs': 10, 'fat': 18, 'tags': ['low_carb']},
        {'meal_name': 'Cauliflower Rice Bowl', 'calories': 190, 'protein': 12, 'carbs': 8, 'fat': 12, 'tags': ['low_carb']},
        {'meal_name': 'Stuffed Bell Peppers', 'calories': 250, 'protein': 18, 'carbs': 14, 'fat': 14, 'tags': ['low_carb']},
        {'meal_name': 'Turkey Lettuce Wraps', 'calories': 200, 'protein': 24, 'carbs': 6, 'fat': 10, 'tags': ['low_carb', 'high_protein']},
        # Healthy fat
        {'meal_name': 'Avocado Toast', 'calories': 280, 'protein': 7, 'carbs': 24, 'fat': 18, 'tags': ['healthy_fat']},
        {'meal_name': 'Trail Mix (Almonds & Walnuts)', 'calories': 300, 'protein': 10, 'carbs': 14, 'fat': 24, 'tags': ['healthy_fat']},
        {'meal_name': 'Chia Seed Pudding', 'calories': 240, 'protein': 6, 'carbs': 20, 'fat': 16, 'tags': ['healthy_fat']},
        {'meal_name': 'Dark Chocolate & Almond Butter', 'calories': 260, 'protein': 7, 'carbs': 16, 'fat': 20, 'tags': ['healthy_fat']},
    ]

    @classmethod
    def get_recommendations(cls, user_id):
        averages = FoodLogRepository.get_weekly_averages(user_id)

        avg_protein = averages.get('avg_protein', 0)
        avg_calories = averages.get('avg_calories', 0)
        avg_carbs = averages.get('avg_carbs', 0)
        avg_fat = averages.get('avg_fat', 0)

        recommendations = []
        seen_meals = set()

        # Determine which tags to recommend
        needed_tags = []
        reasons = {}

        if avg_protein < cls.PROTEIN_LOW:
            needed_tags.append('high_protein')
            reasons['high_protein'] = f'Your average protein ({avg_protein:.0f}g/day) is below {cls.PROTEIN_LOW}g — boost it with protein-rich meals.'

        if avg_calories > cls.CALORIE_HIGH:
            needed_tags.append('low_calorie')
            reasons['low_calorie'] = f'Your average calorie intake ({avg_calories:.0f} kcal/day) is high — try lighter meals.'

        if avg_carbs > cls.CARBS_HIGH:
            needed_tags.append('low_carb')
            reasons['low_carb'] = f'Your carb intake ({avg_carbs:.0f}g/day) is elevated — consider low-carb alternatives.'

        if avg_fat < cls.FAT_LOW:
            needed_tags.append('healthy_fat')
            reasons['healthy_fat'] = f'Your fat intake ({avg_fat:.0f}g/day) is low — add healthy fats to your diet.'

        # If no specific gaps, give general healthy picks
        if not needed_tags:
            needed_tags = ['high_protein', 'low_calorie']
            reasons['high_protein'] = 'Great balance! Here are some nutritious meal ideas to maintain your progress.'
            reasons['low_calorie'] = 'Great balance! Here are some nutritious meal ideas to maintain your progress.'

        for tag in needed_tags:
            for meal in cls.HEALTHY_MEALS:
                if tag in meal['tags'] and meal['meal_name'] not in seen_meals:
                    seen_meals.add(meal['meal_name'])
                    recommendations.append({
                        'meal_name': meal['meal_name'],
                        'calories': meal['calories'],
                        'protein': meal['protein'],
                        'carbs': meal['carbs'],
                        'fat': meal['fat'],
                        'reason_for_recommendation': reasons.get(tag, '')
                    })

        return recommendations[:8]  # Cap at 8 recommendations
