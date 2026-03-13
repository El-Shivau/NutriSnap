# NutriSnap Deployment Guide

## Current Status
✅ **Local App is Running** on `http://127.0.0.1:5000`

### Tech Stack
- **Backend:** Flask (Python 3.11)
- **Database:** SQLite (local) / PostgreSQL (production)
- **ML Model:** TensorFlow/Keras
- **Server:** Gunicorn + Flask development

---

## Running Locally

### Development (Current)
```bash
cd Food-Image-Recognition
./venv/bin/python app.py
```
Visit: `http://127.0.0.1:5000`

### Production (Gunicorn)
```bash
cd Food-Image-Recognition
./venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

---

## Deployment Options

### Option 1: Render (Recommended)
**Free tier available | Easy deployment**

1. Push code to GitHub
2. Connect Render to your GitHub repo
3. Create new Web Service
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
6. Set environment variables:
   - `SECRET_KEY`: Generate a random key
   - `DATABASE_URL`: Keep as SQLite OR use Render PostgreSQL

### Option 2: Heroku
**Heroku free tier has been discontinued**

Alternative: Use Heroku's paid option or Render instead.

### Option 3: DigitalOcean App Platform
**$5/month minimum**

1. Connect GitHub repository
2. Auto-detects Python/Flask
3. Scale as needed
4. PostgreSQL database available

### Option 4: AWS/Google Cloud/Azure
**Pay-as-you-go pricing**

Use container deployment (Docker) for better control.

---

## Database Configuration

### Local Development (Current - SQLite)
```
DATABASE_URL=sqlite:///nutrisnap.db
```
✅ Works perfectly with TensorFlow  
✅ No additional setup needed

### Production with PostgreSQL
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```
⚠️ Note: If deploying with PostgreSQL on Linux, use app server with built-in Python support only, OR convert to cloud functions.

---

## Environment Variables (.env)
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///nutrisnap.db
USDA_API_KEY=DEMO_KEY
HF_API_TOKEN=
```

See `.env.example` for reference.

---

## Quick Deployment to Render

### Steps:
1. **Create GitHub repo** and push code
```bash
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/YOUR-USERNAME/nutrisnap.git
git push -u origin main
```

2. **Go to render.com**
   - Sign up with GitHub
   - New → Web Service
   - Select your repository
   - Name: `nutrisnap`
   - Runtime: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
   - Add environment variables if needed

3. **Deploy** - Render auto-deploys on push

---

## Files for Deployment
- ✅ `wsgi.py` - WSGI entry point for production
- ✅ `Procfile` - Deployment instructions
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment template

---

## Troubleshooting

### App won't start
Check logs in deployment dashboard. Common issues:
- Missing environment variables
- Database connection error
- Port conflicts

### Database errors
- Ensure `DATABASE_URL` is correct
- For PostgreSQL: `psycopg2-binary` must be installed
- For SQLite: Database file permissions

### ML Model issues
- `CUDA_VISIBLE_DEVICES=-1` is set to force CPU
- TensorFlow requires ~500MB memory
- First request may be slow (model loading)

---

## Monitoring & Logs
- **Render:** View real-time logs in dashboard
- **Local:** Check terminal output
- **Errors:** Check `/logs` endpoint if available

---

## Next Steps
1. Deploy to Render (free tier)
2. Test all features on live server
3. Set up custom domain (optional)
4. Configure backups if using database

---

**Your app is production-ready!** 🚀
