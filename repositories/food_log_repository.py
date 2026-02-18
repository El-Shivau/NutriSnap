from models.food_log import FoodLog
from extensions import db
from sqlalchemy import func, extract
from datetime import datetime, timedelta

class FoodLogRepository:
    @staticmethod
    def create(user_id, data):
        log = FoodLog(
            user_id=user_id,
            food_name=data['food_name'],
            calories=data['calories'],
            protein=data['nutrition']['protein'],
            carbs=data['nutrition']['carbohydrates'],
            fat=data['nutrition']['fat'],
            image_url=data.get('image_url')
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_user_logs(user_id, limit=10):
        return FoodLog.query.filter_by(user_id=user_id).order_by(FoodLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_daily_totals(user_id, date=None):
        if date is None:
            date = datetime.utcnow().date()
        
        # Filter by date range (start of day to end of day)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        return db.session.query(
            func.sum(FoodLog.calories).label('total_calories'),
            func.sum(FoodLog.protein).label('total_protein'),
            func.sum(FoodLog.carbs).label('total_carbs'),
            func.sum(FoodLog.fat).label('total_fat')
        ).filter(FoodLog.user_id == user_id, FoodLog.created_at.between(start, end)).first()

    @staticmethod
    def get_weekly_summary(user_id):
        # Group by Date for the last 7 days
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        return db.session.query(
            func.date(FoodLog.created_at).label('date'),
            func.sum(FoodLog.calories).label('calories'),
            func.sum(FoodLog.protein).label('protein')
        ).filter(FoodLog.user_id == user_id, FoodLog.created_at >= start)\
        .group_by(func.date(FoodLog.created_at)).all()

    @staticmethod
    def get_monthly_summary(user_id):
        # Group by Date for the last 30 days
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        return db.session.query(
            func.date(FoodLog.created_at).label('date'),
            func.sum(FoodLog.calories).label('calories'),
            func.sum(FoodLog.protein).label('protein')
        ).filter(FoodLog.user_id == user_id, FoodLog.created_at >= start)\
        .group_by(func.date(FoodLog.created_at)).all()

    @staticmethod
    def get_weekly_totals_all_users():
        """SUM(calories), SUM(protein), COUNT(DISTINCT date) grouped by user_id for leaderboard."""
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        return db.session.query(
            FoodLog.user_id,
            func.sum(FoodLog.calories).label('total_calories'),
            func.sum(FoodLog.protein).label('total_protein'),
            func.count(func.distinct(func.date(FoodLog.created_at))).label('days_logged')
        ).filter(FoodLog.created_at >= start)\
        .group_by(FoodLog.user_id).all()

    @staticmethod
    def get_weekly_averages(user_id):
        """Daily averages for the last 7 days for recommendation engine."""
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        result = db.session.query(
            func.avg(FoodLog.calories).label('avg_calories'),
            func.avg(FoodLog.protein).label('avg_protein'),
            func.avg(FoodLog.carbs).label('avg_carbs'),
            func.avg(FoodLog.fat).label('avg_fat')
        ).filter(FoodLog.user_id == user_id, FoodLog.created_at >= start).first()

        return {
            'avg_calories': float(result.avg_calories or 0),
            'avg_protein': float(result.avg_protein or 0),
            'avg_carbs': float(result.avg_carbs or 0),
            'avg_fat': float(result.avg_fat or 0)
        }
