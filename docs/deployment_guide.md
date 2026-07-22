# NutriSnap – Deployment Guide

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.10+
- PostgreSQL (recommended for production)
- A domain name (optional)
- Nginx (as reverse proxy)

---

## 1. Clone and Setup

```bash
git clone https://github.com/your-username/nutrisnap.git
cd nutrisnap

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set these critical values for production:
```
FLASK_ENV=production
FLASK_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://user:password@localhost:5432/nutrisnap_db
MODEL_PATH=ml/models/food101_v1.keras
BCRYPT_LOG_ROUNDS=12
LOG_LEVEL=WARNING
```

---

## 3. Set Up PostgreSQL Database

```bash
sudo -u postgres psql
CREATE DATABASE nutrisnap_db;
CREATE USER nutrisnap_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nutrisnap_db TO nutrisnap_user;
\q
```

---

## 4. Initialise the Database

```bash
bash scripts/init_db.sh
```

---

## 5. Place the Trained Model

Copy the trained model file to:
```
ml/models/food101_v1.keras
```

Update `MODEL_PATH` in `.env` if using a different version.

---

## 6. Run with Gunicorn

```bash
gunicorn \
  --workers 4 \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  backend.wsgi:app
```

For GPU inference, reduce workers to 1 to avoid OOM errors.

---

## 7. Configure Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/nutrisnap/frontend/static/;
    }

    client_max_body_size 20M;
}
```

---

## 8. Set Up Systemd Service (Auto-restart)

Create `/etc/systemd/system/nutrisnap.service`:

```ini
[Unit]
Description=NutriSnap Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/nutrisnap
Environment="PATH=/path/to/nutrisnap/venv/bin"
ExecStart=/path/to/nutrisnap/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 backend.wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nutrisnap
sudo systemctl start nutrisnap
```
