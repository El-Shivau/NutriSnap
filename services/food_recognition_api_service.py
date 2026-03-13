import base64
import requests
from flask import current_app


class FoodRecognitionAPIService:
    """Uses Hugging Face Inference API with the nateraw/food model.
    
    Free — no API key required for anonymous requests (~30 req/hour).
    Model: ViT fine-tuned on Food-101 dataset (101 classes).
    """

    API_URL = 'https://router.huggingface.co/hf-inference/models/nateraw/food'
    last_error = None

    @staticmethod
    def recognize(image_path):
        """Send image to Hugging Face food classifier.
        
        Returns list of dicts: [{'name': str, 'confidence': float}, ...]
        Or None if API is unavailable.
        """
        try:
            FoodRecognitionAPIService.last_error = None
            # Read raw image bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            headers = {}
            hf_token = current_app.config.get('HF_API_TOKEN', '')
            if not hf_token:
                FoodRecognitionAPIService.last_error = (
                    'Missing HF_API_TOKEN. Add a valid Hugging Face token in Render environment variables.'
                )
                print(f"[FoodAPI] {FoodRecognitionAPIService.last_error}")
                return None

            headers['Authorization'] = f'Bearer {hf_token}'

            print(f"[FoodAPI] Sending image to Hugging Face (nateraw/food)...")
            response = requests.post(
                FoodRecognitionAPIService.API_URL,
                headers=headers,
                data=image_bytes,
                timeout=15
            )

            if response.status_code == 503:
                # Model is loading, might need to wait
                print("[FoodAPI] Model is loading, retrying in 5s...")
                import time
                time.sleep(5)
                response = requests.post(
                    FoodRecognitionAPIService.API_URL,
                    headers=headers,
                    data=image_bytes,
                    timeout=15
                )

            if response.status_code != 200:
                FoodRecognitionAPIService.last_error = (
                    f"HuggingFace API error {response.status_code}: {response.text[:200]}"
                )
                print(f"[FoodAPI] {FoodRecognitionAPIService.last_error}")
                return None

            data = response.json()

            if isinstance(data, dict) and 'error' in data:
                FoodRecognitionAPIService.last_error = f"HuggingFace response error: {data['error']}"
                print(f"[FoodAPI] Error: {data['error']}")
                return None

            if not isinstance(data, list) or len(data) == 0:
                FoodRecognitionAPIService.last_error = 'HuggingFace returned no predictions.'
                print("[FoodAPI] No predictions returned")
                return None

            # Parse result — HF returns [{label, score}, ...]
            results = []
            for item in data[:5]:
                name = item.get('label', '').strip().lower().replace('_', ' ')
                conf = round(float(item.get('score', 0)), 4)
                results.append({'name': name, 'confidence': conf})

            print(f"[FoodAPI] Results:")
            for i, r in enumerate(results[:3], 1):
                print(f"  #{i}: {r['name']} ({r['confidence']*100:.1f}%)")

            return results

        except requests.exceptions.Timeout:
            FoodRecognitionAPIService.last_error = 'HuggingFace request timed out.'
            print("[FoodAPI] Request timed out")
            return None
        except Exception as e:
            FoodRecognitionAPIService.last_error = f"HuggingFace request failed: {e}"
            print(f"[FoodAPI] Error: {e}")
            return None
