import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.ml_service import MLService
from services.food_log_service import FoodLogService
from security.auth import token_required

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/api/scan', methods=['POST'])
@token_required
def scan_image(current_user):
    """Scan an image and return prediction + nutrition. Does NOT log to database."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        try:
            result = MLService.predict(filepath)
            image_url = f"/{upload_folder}/{filename}"
            result['image_url'] = image_url
            # Just return the result — user decides whether to log it
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@scan_bp.route('/api/log', methods=['POST'])
@token_required
def add_to_log(current_user):
    """Explicitly add a scanned result to the user's food log."""
    data = request.get_json()
    if not data or not data.get('food_name'):
        return jsonify({'error': 'Missing food data'}), 400

    prediction_result = {
        'food_name': data['food_name'],
        'calories': data.get('calories', 0),
        'nutrition': {
            'protein': data.get('protein', 0),
            'carbohydrates': data.get('carbs', 0),
            'fat': data.get('fat', 0)
        }
    }
    image_url = data.get('image_url', '')

    FoodLogService.log_food(current_user.id, prediction_result, image_url)
    return jsonify({'message': 'Added to log', 'food_name': data['food_name']})
