from flask import Blueprint, jsonify
from security.auth import token_required
from services.leaderboard_service import LeaderboardService

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user):
    leaderboard = LeaderboardService.get_weekly_leaderboard(current_user.id)
    return jsonify(leaderboard)
