from flask import Blueprint, jsonify, request
from security.auth import token_required
from services.food_log_service import FoodLogService
from repositories.food_log_repository import FoodLogRepository

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    stats = FoodLogService.get_dashboard_stats(current_user.id)
    return jsonify(stats)

@api_bp.route('/api/dashboard/logs', methods=['GET'])
@token_required
def get_recent_logs(current_user):
    logs = FoodLogService.get_recent_logs(current_user.id)
    return jsonify(logs)

@api_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    from models.food_log import FoodLog
    total_logs = FoodLog.query.filter_by(user_id=current_user.id).count()

    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'total_logs': total_logs,
        'joined': current_user.created_at.strftime('%Y-%m-%d'),
        'role': current_user.role
    })
