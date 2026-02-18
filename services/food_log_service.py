from repositories.food_log_repository import FoodLogRepository

class FoodLogService:
    @staticmethod
    def log_food(user_id, prediction_result, image_url):
        # prediction_result matches format from MLService.predict
        return FoodLogRepository.create(user_id, prediction_result)

    @staticmethod
    def get_recent_logs(user_id):
        logs = FoodLogRepository.get_user_logs(user_id)
        return [{
            'food_name': log.food_name,
            'calories': log.calories,
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M'),
            'image_url': log.image_url
        } for log in logs]

    @staticmethod
    def get_dashboard_stats(user_id):
        daily = FoodLogRepository.get_daily_totals(user_id)
        weekly = FoodLogRepository.get_weekly_summary(user_id)
        monthly = FoodLogRepository.get_monthly_summary(user_id)

        return {
            'today': {
                'calories': daily.total_calories or 0,
                'protein': daily.total_protein or 0,
                'carbs': daily.total_carbs or 0,
                'fat': daily.total_fat or 0
            },
            'weekly': [{'date': str(r.date), 'calories': r.calories, 'protein': r.protein} for r in weekly],
            'monthly': [{'date': str(r.date), 'calories': r.calories, 'protein': r.protein} for r in monthly]
        }
