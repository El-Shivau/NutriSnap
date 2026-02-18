import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_nutrisnap_2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///nutrisnap.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'

    # USDA FoodData Central — DEMO_KEY works instantly, no signup
    # For higher limits, get a free key at https://fdc.nal.usda.gov/api-key-signup.html
    USDA_API_KEY = os.environ.get('USDA_API_KEY') or 'DEMO_KEY'

    # Hugging Face (optional) — works without key, but key gives higher rate limits
    # Get a free token at https://huggingface.co/settings/tokens
    HF_API_TOKEN = os.environ.get('HF_API_TOKEN') or ''
