"""
NutriSnap Backend Package
=========================

This package contains the complete Flask web application for NutriSnap.

Architecture follows a clean, layered approach:

    Controllers  →  receive HTTP requests, call services, return responses
    Services     →  contain all business logic
    Repositories →  handle all database access via SQLAlchemy
    Models       →  define SQLAlchemy ORM models
    Utils        →  reusable helpers shared across layers

The application is created via the create_app() factory in app.py.
"""
