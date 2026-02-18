from repositories.friendship_repository import FriendshipRepository
from repositories.user_repository import UserRepository
from repositories.food_log_repository import FoodLogRepository


class FriendshipService:
    @staticmethod
    def add_friend(user_id, friend_username):
        """Add a friend by username. Returns success/error dict."""
        friend = UserRepository.get_by_username(friend_username)
        if not friend:
            return {'error': 'User not found'}, 404

        if friend.id == user_id:
            return {'error': 'You cannot add yourself'}, 400

        if FriendshipRepository.are_friends(user_id, friend.id):
            return {'error': 'Already friends'}, 400

        FriendshipRepository.add_friend(user_id, friend.id)
        return {'message': f'Added {friend.username} as friend'}, 201

    @staticmethod
    def get_friends_list(user_id):
        """Return list of friend info dicts."""
        friendships = FriendshipRepository.get_friends(user_id)
        return [{
            'id': f.friend.id,
            'username': f.friend.username,
            'since': f.created_at.strftime('%Y-%m-%d')
        } for f in friendships]

    @staticmethod
    def get_friend_analytics(user_id, friend_id):
        """Get a friend's weekly/monthly stats and recent meals."""
        # Verify friendship
        if not FriendshipRepository.are_friends(user_id, friend_id):
            return {'error': 'Not friends with this user'}, 403

        friend = UserRepository.get_by_id(friend_id)
        if not friend:
            return {'error': 'User not found'}, 404

        # Reuse existing repository methods
        daily = FoodLogRepository.get_daily_totals(friend_id)
        weekly = FoodLogRepository.get_weekly_summary(friend_id)
        monthly = FoodLogRepository.get_monthly_summary(friend_id)
        logs = FoodLogRepository.get_user_logs(friend_id, limit=15)

        weekly_totals = {
            'calories': sum(r.calories or 0 for r in weekly),
            'protein': sum(r.protein or 0 for r in weekly)
        }
        monthly_totals = {
            'calories': sum(r.calories or 0 for r in monthly),
            'protein': sum(r.protein or 0 for r in monthly)
        }

        return {
            'username': friend.username,
            'today': {
                'calories': daily.total_calories or 0 if daily else 0,
                'protein': daily.total_protein or 0 if daily else 0,
            },
            'weekly': {
                'calories': round(weekly_totals['calories'], 1),
                'protein': round(weekly_totals['protein'], 1),
                'daily': [{'date': str(r.date), 'calories': r.calories, 'protein': r.protein} for r in weekly]
            },
            'monthly': {
                'calories': round(monthly_totals['calories'], 1),
                'protein': round(monthly_totals['protein'], 1),
            },
            'recent_meals': [{
                'food_name': log.food_name,
                'calories': log.calories,
                'protein': log.protein,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M'),
                'image_url': log.image_url
            } for log in logs]
        }, 200
