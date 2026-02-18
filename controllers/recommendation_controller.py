from flask import Blueprint, jsonify
from security.auth import token_required
from services.recommendation_service import RecommendationService

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    recommendations = RecommendationService.get_recommendations(current_user.id)
    return jsonify(recommendations)
