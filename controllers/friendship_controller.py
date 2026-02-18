from flask import Blueprint, jsonify, request
from security.auth import token_required
from services.friendship_service import FriendshipService

friendship_bp = Blueprint('friendship', __name__)


@friendship_bp.route('/api/friends/add', methods=['POST'])
@token_required
def add_friend(current_user):
    data = request.get_json()
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    result, status = FriendshipService.add_friend(current_user.id, username)
    return jsonify(result), status


@friendship_bp.route('/api/friends', methods=['GET'])
@token_required
def get_friends(current_user):
    friends = FriendshipService.get_friends_list(current_user.id)
    return jsonify(friends)


@friendship_bp.route('/api/friends/<int:friend_id>/analytics', methods=['GET'])
@token_required
def get_friend_analytics(current_user, friend_id):
    result, status = FriendshipService.get_friend_analytics(current_user.id, friend_id)
    return jsonify(result), status
