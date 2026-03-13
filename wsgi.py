"""
WSGI entry point for production deployment with Gunicorn.
Usage: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
