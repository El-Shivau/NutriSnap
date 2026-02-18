import requests
from flask import current_app


class NutritionAPIService:
    """Fetches nutrition data from USDA FoodData Central API.
    
    Free — uses DEMO_KEY by default (rate-limited but works instantly).
    Docs: https://fdc.nal.usda.gov/api-guide
    """

    BASE_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search'

    @staticmethod
    def lookup(food_name):
        """Query USDA FoodData Central for nutrition info.
        
        Returns dict with standardized nutrition info, or None on failure.
        """
        api_key = current_app.config.get('USDA_API_KEY', 'DEMO_KEY')

        try:
            params = {
                'api_key': api_key,
                'query': food_name,
                'pageSize': 1,
                'dataType': 'Survey (FNDDS)'  # Best for common foods
            }

            print(f"[NutritionAPI] Querying USDA for: '{food_name}'")
            response = requests.get(
                NutritionAPIService.BASE_URL,
                params=params,
                timeout=8
            )

            if response.status_code != 200:
                print(f"[NutritionAPI] API returned {response.status_code}")
                return None

            data = response.json()
            foods = data.get('foods', [])

            if not foods:
                # Try broader search without dataType filter
                params.pop('dataType', None)
                response = requests.get(
                    NutritionAPIService.BASE_URL,
                    params=params,
                    timeout=8
                )
                if response.status_code == 200:
                    data = response.json()
                    foods = data.get('foods', [])

            if not foods:
                print(f"[NutritionAPI] No results for '{food_name}'")
                return None

            # Parse top result's nutrients
            food = foods[0]
            nutrients = {n['nutrientName']: n.get('value', 0) for n in food.get('foodNutrients', [])}

            calories = nutrients.get('Energy', 0)
            protein = nutrients.get('Protein', 0)
            fat = nutrients.get('Total lipid (fat)', 0)
            carbs = nutrients.get('Carbohydrate, by difference', 0)
            fiber = nutrients.get('Fiber, total dietary', 0)
            sugar = nutrients.get('Sugars, total including NLEA', 
                     nutrients.get('Total Sugars', 0))
            serving = food.get('servingSize', 100)
            serving_unit = food.get('servingSizeUnit', 'g')

            result = {
                'calories': round(float(calories), 1),
                'protein': round(float(protein), 1),
                'carbohydrates': round(float(carbs), 1),
                'fat': round(float(fat), 1),
                'fiber': round(float(fiber), 1),
                'sugar': round(float(sugar), 1),
                'serving_size_g': round(float(serving), 1),
                'serving_unit': serving_unit,
                'source': 'usda_fdc'
            }
            print(f"[NutritionAPI] Got: {result['calories']} kcal, "
                  f"{result['protein']}g protein, "
                  f"{result['carbohydrates']}g carbs, "
                  f"{result['fat']}g fat "
                  f"(per {result['serving_size_g']}{serving_unit})")
            return result

        except requests.exceptions.Timeout:
            print("[NutritionAPI] Request timed out — falling back to local DB")
            return None
        except Exception as e:
            print(f"[NutritionAPI] Error: {e} — falling back to local DB")
            return None
