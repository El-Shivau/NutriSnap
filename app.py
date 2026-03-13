import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from flask import Flask
from config import Config
from extensions import db
from services.ml_service import MLService

# Import Controllers
from controllers.auth_controller import auth_bp
from controllers.api_controller import api_bp
from controllers.scan_controller import scan_bp
from controllers.view_controller import view_bp
from controllers.leaderboard_controller import leaderboard_bp
from controllers.recommendation_controller import recommendation_bp
from controllers.friendship_controller import friendship_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)

    # Initialize ML Service & Database
    with app.app_context():
        MLService.initialize()

        # Import models so db.create_all() creates their tables
        from models.nutrition_info import NutritionInfo
        from models.friendship import Friendship
        db.create_all()  # Create tables if not exist

        # Seed nutrition data from CSV into DB
        from services.nutrition_service import NutritionService
        NutritionService.seed_from_csv()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(friendship_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
