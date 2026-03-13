import requests
from flask import current_app


class BiteAIService:
    """Food recognition via BiteAI-compatible HTTP API."""

    last_error = None

    @staticmethod
    def _normalize_predictions(payload):
        candidates = None

        if isinstance(payload, list):
            candidates = payload
        elif isinstance(payload, dict):
            for key in ('predictions', 'results', 'data', 'foods', 'items'):
                value = payload.get(key)
                if isinstance(value, list):
                    candidates = value
                    break

        if not candidates:
            return []

        parsed = []
        for item in candidates:
            if not isinstance(item, dict):
                continue

            name = (
                item.get('label')
                or item.get('name')
                or item.get('food')
                or item.get('class')
                or item.get('category')
                or ''
            )
            score = (
                item.get('confidence')
                or item.get('score')
                or item.get('probability')
                or item.get('prob')
                or 0
            )

            try:
                confidence = float(score)
            except Exception:
                confidence = 0.0

            name = str(name).strip().lower().replace('_', ' ')
            if not name:
                continue

            parsed.append({'name': name, 'confidence': round(confidence, 4)})

        parsed.sort(key=lambda entry: entry['confidence'], reverse=True)
        return parsed[:5]

    @staticmethod
    def recognize(image_path):
        BiteAIService.last_error = None

        api_url = (current_app.config.get('BITEAI_API_URL') or '').strip()
        api_key = (current_app.config.get('BITEAI_API_KEY') or '').strip()

        if not api_url:
            BiteAIService.last_error = 'Missing BITEAI_API_URL in environment variables.'
            return None

        if not api_key:
            BiteAIService.last_error = 'Missing BITEAI_API_KEY in environment variables.'
            return None

        headers = {
            'Authorization': f'Bearer {api_key}',
            'x-api-key': api_key,
            'Accept': 'application/json'
        }

        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                response = requests.post(api_url, headers=headers, files=files, timeout=30)

            if response.status_code >= 400:
                BiteAIService.last_error = f'BiteAI API error {response.status_code}: {response.text[:200]}'
                print(f"[BiteAI] {BiteAIService.last_error}")
                return None

            try:
                payload = response.json()
            except Exception:
                BiteAIService.last_error = 'BiteAI returned non-JSON response.'
                print(f"[BiteAI] {BiteAIService.last_error}")
                return None

            predictions = BiteAIService._normalize_predictions(payload)
            if not predictions:
                BiteAIService.last_error = 'BiteAI returned no usable predictions.'
                print(f"[BiteAI] {BiteAIService.last_error}")
                return None

            print('[BiteAI] Results:')
            for rank, prediction in enumerate(predictions[:3], 1):
                print(f"  #{rank}: {prediction['name']} ({prediction['confidence']*100:.1f}%)")

            return predictions

        except requests.exceptions.Timeout:
            BiteAIService.last_error = 'BiteAI request timed out.'
            print(f"[BiteAI] {BiteAIService.last_error}")
            return None
        except Exception as error:
            BiteAIService.last_error = f'BiteAI request failed: {error}'
            print(f"[BiteAI] {BiteAIService.last_error}")
            return None
