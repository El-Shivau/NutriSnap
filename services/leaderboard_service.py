from repositories.food_log_repository import FoodLogRepository
from repositories.user_repository import UserRepository
from repositories.friendship_repository import FriendshipRepository


class LeaderboardService:
    # Default goals
    PROTEIN_GOAL = 50  # grams per day → 350/week
    CALORIE_MIN = 1500
    CALORIE_MAX = 2500

    @classmethod
    def get_weekly_leaderboard(cls, user_id):
        """Rank only the current user + their friends."""
        # Get friend IDs + self
        friend_ids = FriendshipRepository.get_friend_ids(user_id)
        participant_ids = set(friend_ids + [user_id])

        # Get all weekly data
        weekly_data = FoodLogRepository.get_weekly_totals_all_users()

        # Build lookup: user_id -> stats
        user_stats = {}
        for row in weekly_data:
            if row.user_id in participant_ids:
                user_stats[row.user_id] = {
                    'total_calories': row.total_calories or 0,
                    'total_protein': row.total_protein or 0,
                    'days_logged': row.days_logged or 0
                }

        leaderboard = []
        for uid in participant_ids:
            user = UserRepository.get_by_id(uid)
            if not user:
                continue

            stats = user_stats.get(uid, {
                'total_calories': 0, 'total_protein': 0, 'days_logged': 0
            })

            weekly_protein = stats['total_protein']
            days_logged = stats['days_logged']
            total_calories = stats['total_calories']
            avg_daily_cals = total_calories / max(days_logged, 1)

            # Scoring formula
            protein_score = min((weekly_protein / (cls.PROTEIN_GOAL * 7)) * 40, 40)
            consistency_score = (days_logged / 7) * 30
            calorie_balance_score = 30 if cls.CALORIE_MIN <= avg_daily_cals <= cls.CALORIE_MAX else 0

            final_score = round(protein_score + consistency_score + calorie_balance_score, 1)

            leaderboard.append({
                'user_id': uid,
                'username': user.username,
                'score': final_score,
                'protein': round(weekly_protein, 1),
                'calories': round(total_calories, 1),
                'days_logged': days_logged,
                'is_self': uid == user_id
            })

        # Sort descending by score
        leaderboard.sort(key=lambda x: x['score'], reverse=True)

        # Add ranks
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1

        return leaderboard
