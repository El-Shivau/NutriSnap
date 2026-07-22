# NutriSnap – System Architecture

## Overview

NutriSnap follows a **clean, layered architecture** that clearly separates concerns between the machine learning pipeline and the web application backend.

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│              Bootstrap 5 UI — HTML + CSS + JS               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests
┌──────────────────────────▼──────────────────────────────────┐
│                    FLASK WEB APPLICATION                     │
│                                                              │
│   Controllers  →  Services  →  Repositories  →  Database    │
│      (routes)     (logic)        (queries)      (SQLite/PG)  │
│                                                              │
│                        │                                     │
│                        ▼ calls                               │
│                  ML Inference Module                         │
│                  (ml/inference/predictor.py)                 │
└──────────────────────────────────────────────────────────────┘
                           │ model.predict()
┌──────────────────────────▼──────────────────────────────────┐
│                   ML PIPELINE (Independent)                  │
│                                                              │
│   Dataset → Preprocessing → Training → Evaluation           │
│                    ↓                                         │
│            food101_v1.keras  (saved model)                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Controllers
- Receive HTTP request
- Validate file uploads (type, size)
- Call the appropriate Service
- Return HTTP response (render template or redirect)
- **No** business logic here

### Services
- Contain all business logic
- Coordinate between Repositories and the ML module
- Called by Controllers only
- **No** direct database queries here

### Repositories
- Handle all SQLAlchemy database queries
- Called by Services only
- No business logic — pure data access

### Models
- SQLAlchemy ORM table definitions
- Contain `to_dict()` serialisation methods
- No business logic

### ML Inference Module
- The **only** bridge between Flask and TensorFlow
- Loaded once at startup, reused for each request
- Returns structured prediction dictionaries

---

## Request Flow — Food Recognition

```
User uploads image
        │
        ▼
FoodController.upload() ─── validates file ──→ 400 if invalid
        │
        ▼
FoodService.save_image() ──────── saves to backend/uploads/
        │
        ▼
FoodService.predict_food()
        │
        ▼
Predictor.predict(image_path) ─── loads model (once) ──→ runs model.predict()
        │
        ▼
Returns { food_name, confidence, top_3 }
        │
        ▼
NutritionService.get_by_food_name()
        │
        ▼
NutritionRepository.find_by_food_name()
        │
        ▼
Returns Nutrition record
        │
        ▼
FoodController renders prediction.html
        │
User confirms → FoodService.create_food_log() → FoodLogRepository.save()
        │
        ▼
Redirect to history page
```

---

## Security Architecture

| Concern | Mechanism |
|---------|-----------|
| Password storage | bcrypt hash (never plaintext) |
| Session management | Flask-Login + signed cookies |
| CSRF protection | Flask-WTF (all POST forms) |
| File upload | Extension whitelist + size limit |
| Filename sanitisation | `werkzeug.utils.secure_filename` |
| Secrets | Environment variables via `.env` |
| SQL injection | SQLAlchemy ORM (parameterised queries) |
