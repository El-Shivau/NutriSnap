# NutriSnap 🍕🥗🍜

**AI-Powered Food Image Recognition with Nutritional Analysis**

NutriSnap is a full-stack web application that uses a self-trained deep learning model (EfficientNetB0) to recognise food from images and instantly provide detailed nutritional information. Built as a university capstone project, it demonstrates computer vision, deep learning, full-stack development, and production-ready software practices.

---

## ✨ Features

| Feature | Status |
|---------|--------|
| User Authentication (register, login, logout) | ✅ Phase 5 |
| Food Image Upload & Recognition | ✅ Phase 7 |
| Nutritional Information Display | ✅ Phase 7 |
| Food Logging | ✅ Phase 7 |
| Dashboard & History | ✅ Phase 6 |
| User Profiles | ✅ Phase 6 |
| Responsive UI | ✅ Phase 6 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **ML Model** | TensorFlow / Keras — EfficientNetB0 (transfer learning) |
| **Dataset** | Food-101 (101 food classes, 101,000 images) |
| **Backend** | Python 3.10+, Flask 3.x |
| **Database** | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy |
| **Authentication** | Flask-Login + Flask-Bcrypt |
| **Frontend** | HTML5, Bootstrap 5, Vanilla JS |
| **Testing** | pytest + pytest-flask |
| **Deployment** | Gunicorn + any Linux host |

---

## 📁 Project Structure

```
NutriSnap/
├── backend/                  # Flask web application
│   ├── config/               # Environment-based configuration
│   ├── controllers/          # Route handlers (thin layer)
│   ├── services/             # Business logic
│   ├── repositories/         # Database access layer
│   ├── models/               # SQLAlchemy ORM models
│   ├── utils/                # Shared helpers (logger, validators)
│   ├── app.py                # Application factory
│   ├── extensions.py         # Shared Flask extensions
│   └── wsgi.py               # Production WSGI entry point
│
├── frontend/                 # Templates & static assets
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
│
├── ml/                       # Machine learning (independent of Flask)
│   ├── dataset/              # Dataset download instructions
│   ├── preprocessing/        # Image preprocessing module
│   ├── training/             # Training pipeline
│   ├── models/               # Saved model files (*.keras)
│   ├── inference/            # Prediction module
│   └── evaluation/           # Evaluation scripts & reports
│
├── data/
│   ├── nutrition/            # nutrition_data.json (101 food classes)
│   └── seeds/                # DB seeder scripts
│
├── docs/                     # Project documentation
├── tests/                    # Unit & integration tests
├── scripts/                  # Shell helper scripts
├── .env.example              # Environment variable template
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development & training extras
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10 or higher
- Git
- (Optional) PostgreSQL for production

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nutrisnap.git
cd nutrisnap
```

### 2. Create & Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
# For development / model training:
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 5. Initialise the Database

```bash
bash scripts/init_db.sh
```

### 6. Run the Development Server

```bash
bash scripts/run_dev.sh
# Or directly:
flask --app backend.wsgi run --debug
```

Visit **http://127.0.0.1:5000** in your browser.

---

## 🧠 Model Training

See [`docs/model_training_guide.md`](docs/model_training_guide.md) for the full guide.

Quick summary:
1. Download Food-101 dataset (see [`ml/dataset/README.md`](ml/dataset/README.md))
2. Run preprocessing pipeline
3. Train with `python ml/training/train.py`
4. Evaluate with `python ml/evaluation/evaluate.py`
5. Saved model appears at `ml/models/food101_v1.keras`

---

## 🧪 Running Tests

```bash
pytest tests/ -v
# With coverage:
pytest tests/ --cov=backend --cov-report=html
```

---

## 📦 Deployment

See [`docs/deployment_guide.md`](docs/deployment_guide.md) for the full deployment guide.

Quick summary for Gunicorn:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 backend.wsgi:app
```

---

## 🗺️ Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project setup, structure, environment, docs | ✅ Complete |
| 2 | Dataset download, EDA, preprocessing module | 🔲 Upcoming |
| 3 | EfficientNetB0 training, fine-tuning, evaluation | 🔲 Upcoming |
| 4 | Inference module & prediction API | 🔲 Upcoming |
| 5 | Flask backend — auth, DB, recognition endpoints | 🔲 Upcoming |
| 6 | Frontend — Bootstrap UI, upload, dashboard | 🔲 Upcoming |
| 7 | Full integration — model + backend + frontend | 🔲 Upcoming |
| 8 | Testing — unit, integration, frontend | 🔲 Upcoming |
| 9 | Deployment — Gunicorn, production config | 🔲 Upcoming |

---

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [Database Schema](docs/database_schema.md)
- [API Reference](docs/api_reference.md)
- [Model Training Guide](docs/model_training_guide.md)
- [Deployment Guide](docs/deployment_guide.md)

---

## 📄 License

This project is for educational purposes. Feel free to use it as a reference or starting point for your own projects.

---

## 👥 Authors

- **Your Name** — *Full-stack development & ML pipeline*

---

> **Note:** The Food-101 dataset is required for training and is NOT included in this repository due to its size (~5 GB). See [`ml/dataset/README.md`](ml/dataset/README.md) for download instructions.
