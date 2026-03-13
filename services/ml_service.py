import os
import csv


class MLService:
    nutrition_table = {}
    CONFIDENCE_THRESHOLD = 0.60
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    LABEL_ALIASES = {
        'takoyaki': 'octopus balls',
    }

    @classmethod
    def initialize(cls):
        if not cls.nutrition_table:
            cls.load_nutrition_data()

    @classmethod
    def load_nutrition_data(cls):
        csv_path = os.path.join(cls.BASE_DIR, 'nutrition101.csv')
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                name = row[1].strip().lower().replace('_', ' ')
                protein = float(row[2])
                fat = float(row[4])
                carbs = float(row[5])
                calories = round((protein * 4) + (carbs * 4) + (fat * 9), 2)

                cls.nutrition_table[name] = {
                    'protein': protein,
                    'calcium': float(row[3]),
                    'fat': fat,
                    'carbohydrates': carbs,
                    'vitamins': float(row[6]),
                    'calories_per_100g': calories
                }

        print(f"Nutrition data loaded: {len(cls.nutrition_table)} entries")

    @classmethod
    def _normalize_label(cls, label_str):
        return label_str.strip().lower().replace('_', ' ')

    @classmethod
    def _find_nutrition(cls, food_name):
        normalized = cls._normalize_label(food_name)

        if normalized in cls.LABEL_ALIASES:
            normalized = cls.LABEL_ALIASES[normalized]

        if normalized in cls.nutrition_table:
            return cls.nutrition_table[normalized]

        best_match = None
        best_score = 0
        for key in cls.nutrition_table:
            if normalized in key or key in normalized:
                score = len(key)
                if score > best_score:
                    best_score = score
                    best_match = key

        if best_match:
            print(f"  [Nutrition] Fuzzy match: '{food_name}' -> '{best_match}'")
            return cls.nutrition_table[best_match]

        print(f"  [Nutrition] No match found for: '{food_name}'")
        return None

    @classmethod
    def predict(cls, image_path):
        cls.initialize()

        food_name = None
        confidence = 0.0
        top_3 = []
        recognition_source = 'none'

        try:
            from flask import current_app
            from services.bite_ai_service import BiteAIService
            from services.food_recognition_api_service import FoodRecognitionAPIService

            provider = (current_app.config.get('FOOD_RECOGNITION_PROVIDER', 'biteai') or 'biteai').lower()
            api_predictions = None
            error_messages = []

            if provider in ('biteai', 'auto'):
                api_predictions = BiteAIService.recognize(image_path)
                if api_predictions:
                    recognition_source = 'biteai_api'
                elif BiteAIService.last_error:
                    error_messages.append(BiteAIService.last_error)

            if not api_predictions and provider in ('huggingface', 'auto', 'biteai'):
                api_predictions = FoodRecognitionAPIService.recognize(image_path)
                if api_predictions:
                    recognition_source = 'huggingface_api'
                elif FoodRecognitionAPIService.last_error:
                    error_messages.append(FoodRecognitionAPIService.last_error)

            if api_predictions and len(api_predictions) > 0:
                best = api_predictions[0]
                food_name = best['name']
                confidence = best['confidence']
                if recognition_source == 'none':
                    recognition_source = 'api'
                top_3 = [
                    {'name': p['name'], 'prob': p['confidence']}
                    for p in api_predictions[:3]
                ]
                print(f"[ML] API-only result: {food_name} ({confidence*100:.1f}%)")
            else:
                detailed_error = ' | '.join(error_messages).strip() or 'Food recognition API is unavailable or returned no result.'
                return {
                    'food_name': 'Unknown',
                    'confidence': 0.0,
                    'low_confidence': True,
                    'nutrition': {
                        'protein': 0,
                        'carbohydrates': 0,
                        'fat': 0,
                        'fiber': 0,
                        'sugar': 0,
                        'serving_size_g': 0
                    },
                    'calories': 0,
                    'message': detailed_error,
                    'recognition_source': 'none',
                    'nutrition_source': 'none',
                    'top_3': []
                }
        except Exception as error:
            return {
                'food_name': 'Unknown',
                'confidence': 0.0,
                'low_confidence': True,
                'nutrition': {
                    'protein': 0,
                    'carbohydrates': 0,
                    'fat': 0,
                    'fiber': 0,
                    'sugar': 0,
                    'serving_size_g': 0
                },
                'calories': 0,
                'message': f'Food recognition API error: {error}',
                'recognition_source': 'none',
                'nutrition_source': 'none',
                'top_3': []
            }

        nutrition_data = None
        calories = 0
        nutrition_source = 'none'

        try:
            from services.nutrition_api_service import NutritionAPIService
            api_result = NutritionAPIService.lookup(food_name)
            if api_result:
                nutrition_data = {
                    'protein': api_result['protein'],
                    'carbohydrates': api_result['carbohydrates'],
                    'fat': api_result['fat'],
                    'fiber': api_result.get('fiber', 0),
                    'sugar': api_result.get('sugar', 0),
                    'serving_size_g': api_result.get('serving_size_g', 100)
                }
                calories = api_result['calories']
                nutrition_source = 'api'
        except Exception as e:
            print(f"[ML] Nutrition API failed: {e}")

        if nutrition_data is None:
            local = cls._find_nutrition(food_name)
            if local:
                nutrition_data = {
                    'protein': local['protein'],
                    'carbohydrates': local['carbohydrates'],
                    'fat': local['fat'],
                    'fiber': 0,
                    'sugar': 0,
                    'serving_size_g': 100
                }
                calories = local['calories_per_100g']
                nutrition_source = 'local_db'

        if nutrition_data is None:
            nutrition_data = {
                'protein': 0,
                'carbohydrates': 0,
                'fat': 0,
                'fiber': 0,
                'sugar': 0,
                'serving_size_g': 0
            }
            nutrition_source = 'none'

        return {
            'food_name': food_name,
            'confidence': round(confidence, 4),
            'low_confidence': False,
            'nutrition': nutrition_data,
            'calories': round(calories, 2),
            'recognition_source': recognition_source,
            'nutrition_source': nutrition_source,
            'top_3': top_3
        }
