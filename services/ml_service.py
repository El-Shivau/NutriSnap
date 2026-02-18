import os
import csv
import math
import numpy as np
import tensorflow
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


class MLService:
    model = None
    nutrition_table = {}
    label = []
    CONFIDENCE_THRESHOLD = 0.60  # 60% minimum confidence

    @classmethod
    def initialize(cls):
        if cls.model is None:
            print("Loading ML Model...")
            tensorflow.keras.backend.clear_session()
            model_path = os.path.join(os.getcwd(), 'best_model_101class.hdf5')
            cls.model = load_model(model_path, compile=False)
            print(f"Model loaded successfully. Input shape: {cls.model.input_shape}")

            cls.load_nutrition_data()
            cls.load_labels()

    @classmethod
    def load_nutrition_data(cls):
        csv_path = os.path.join(os.getcwd(), 'nutrition101.csv')
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                # Normalize name: lowercase, strip whitespace, replace underscores
                name = row[1].strip().lower().replace('_', ' ')
                protein = float(row[2])
                fat = float(row[4])
                carbs = float(row[5])
                # Calories: Protein*4 + Carbs*4 + Fat*9 (per 100g)
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
    def load_labels(cls):
        cls.label = [
            'apple pie', 'baby back ribs', 'baklava', 'beef carpaccio',
            'beef tartare', 'beet salad', 'beignets', 'bibimbap',
            'bread pudding', 'breakfast burrito', 'bruschetta', 'caesar salad',
            'cannoli', 'caprese salad', 'carrot cake', 'ceviche',
            'cheese plate', 'cheesecake', 'chicken curry', 'chicken quesadilla',
            'chicken wings', 'chocolate cake', 'chocolate mousse', 'churros',
            'clam chowder', 'club sandwich', 'crab cakes', 'creme brulee',
            'croque madame', 'cup cakes', 'deviled eggs', 'donuts',
            'dumplings', 'edamame', 'eggs benedict', 'escargots',
            'falafel', 'filet mignon', 'fish and_chips', 'foie gras',
            'french fries', 'french onion soup', 'french toast', 'fried calamari',
            'fried rice', 'frozen yogurt', 'garlic bread', 'gnocchi',
            'greek salad', 'grilled cheese sandwich', 'grilled salmon', 'guacamole',
            'gyoza', 'hamburger', 'hot and sour soup', 'hot dog',
            'huevos rancheros', 'hummus', 'ice cream', 'lasagna',
            'lobster bisque', 'lobster roll sandwich', 'macaroni and cheese', 'macarons',
            'miso soup', 'mussels', 'nachos', 'omelette',
            'onion rings', 'oysters', 'pad thai', 'paella',
            'pancakes', 'panna cotta', 'peking duck', 'pho',
            'pizza', 'pork chop', 'poutine', 'prime rib',
            'pulled pork sandwich', 'ramen', 'ravioli', 'red velvet cake',
            'risotto', 'samosa', 'sashimi', 'scallops',
            'seaweed salad', 'shrimp and grits', 'spaghetti bolognese',
            'spaghetti carbonara', 'spring rolls', 'steak',
            'strawberry shortcake', 'sushi', 'tacos', 'takoyaki',
            'tiramisu', 'tuna tartare', 'waffles'
        ]
        # Labels MUST be in alphabetical order to match Food-101 model output
        # Do NOT sort — the list above is already in correct order

    @classmethod
    def _normalize_label(cls, label_str):
        """Normalize a label for nutrition table lookup."""
        return label_str.strip().lower().replace('_', ' ')

    # Alias map: model label -> nutrition CSV label
    LABEL_ALIASES = {
        'takoyaki': 'octopus balls',
    }

    @classmethod
    def _find_nutrition(cls, food_name):
        """Find nutrition data with exact match, then fallback to partial match."""
        normalized = cls._normalize_label(food_name)

        # 0. Check alias
        if normalized in cls.LABEL_ALIASES:
            normalized = cls.LABEL_ALIASES[normalized]

        # 1. Exact match
        if normalized in cls.nutrition_table:
            return cls.nutrition_table[normalized]

        # 2. Partial/fuzzy match — find best substring match
        best_match = None
        best_score = 0
        for key in cls.nutrition_table:
            # Check if one contains the other
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
        if cls.model is None:
            cls.initialize()

        food_name = None
        confidence = 0.0
        top_3 = []
        recognition_source = 'local_model'

        # ═══════════════════════════════════════
        # STEP 1: Food Recognition
        # ═══════════════════════════════════════

        # --- Try Hugging Face Food API first ---
        try:
            from services.food_recognition_api_service import FoodRecognitionAPIService
            api_predictions = FoodRecognitionAPIService.recognize(image_path)

            if api_predictions and len(api_predictions) > 0:
                best = api_predictions[0]
                if best['confidence'] >= cls.CONFIDENCE_THRESHOLD:
                    food_name = best['name']
                    confidence = best['confidence']
                    recognition_source = 'huggingface_api'
                    top_3 = [
                        {'name': p['name'], 'prob': p['confidence']}
                        for p in api_predictions[:3]
                    ]
                    print(f"[ML] Using HuggingFace API result: {food_name} ({confidence*100:.1f}%)")
                else:
                    print(f"[ML] API top result below threshold: {best['name']} ({best['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"[ML] HuggingFace API failed: {e}")

        # --- Fallback to local model ---
        if food_name is None:
            print("[ML] Using local model...")
            img = image.load_img(image_path, target_size=(200, 200), color_mode='rgb')
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0

            pred = cls.model.predict(img_array, verbose=0)

            # Handle NaN
            if np.any(np.isnan(pred)):
                print("[ML] WARNING: NaN in predictions")
                return {
                    'food_name': 'Unknown',
                    'confidence': 0.0,
                    'low_confidence': True,
                    'nutrition': {'protein': 0, 'carbohydrates': 0, 'fat': 0,
                                  'fiber': 0, 'sugar': 0, 'serving_size_g': 0},
                    'calories': 0,
                    'message': 'Food not confidently recognized',
                    'recognition_source': 'none',
                    'nutrition_source': 'none',
                    'top_3': []
                }

            # Softmax if needed
            if abs(np.sum(pred[0]) - 1.0) > 0.1:
                pred = tensorflow.nn.softmax(pred).numpy()

            top_indices = np.argsort(pred[0])[-3:][::-1]
            food_name = cls.label[top_indices[0]]
            confidence = float(pred[0][top_indices[0]])
            recognition_source = 'local_model'

            top_3 = [
                {'name': cls.label[idx], 'prob': float(pred[0][idx])}
                for idx in top_indices
            ]

            print(f"\n[ML] Local Model Results:")
            for rank, idx in enumerate(top_indices, 1):
                print(f"  #{rank}: {cls.label[idx]} ({pred[0][idx]*100:.1f}%)")

        # --- Confidence Check ---
        if confidence < cls.CONFIDENCE_THRESHOLD:
            print(f"[ML] Low confidence: {confidence*100:.1f}%")
            return {
                'food_name': food_name,
                'confidence': round(confidence, 4),
                'low_confidence': True,
                'nutrition': {'protein': 0, 'carbohydrates': 0, 'fat': 0,
                              'fiber': 0, 'sugar': 0, 'serving_size_g': 0},
                'calories': 0,
                'message': f'Food not confidently recognized ({confidence*100:.0f}% confidence). Best guess: {food_name}',
                'recognition_source': recognition_source,
                'nutrition_source': 'none',
                'top_3': top_3
            }

        # ═══════════════════════════════════════
        # STEP 2: Nutrition Lookup
        # ═══════════════════════════════════════
        nutrition_data = None
        calories = 0
        nutrition_source = 'none'

        # --- Try CalorieNinja API ---
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

        # --- Fallback to local DB ---
        if nutrition_data is None:
            local = cls._find_nutrition(food_name)
            if local:
                nutrition_data = {
                    'protein': local['protein'],
                    'carbohydrates': local['carbohydrates'],
                    'fat': local['fat'],
                    'fiber': 0, 'sugar': 0, 'serving_size_g': 100
                }
                calories = local['calories_per_100g']
                nutrition_source = 'local_db'

        # --- Nothing found ---
        if nutrition_data is None:
            nutrition_data = {
                'protein': 0, 'carbohydrates': 0, 'fat': 0,
                'fiber': 0, 'sugar': 0, 'serving_size_g': 0
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


