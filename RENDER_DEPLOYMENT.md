# NutriSnap - Deployment to Render.com

## Prerequisites
- GitHub account (create one at https://github.com/signup if you don't have it)
- Render account (sign up at https://render.com - free forever)

---

## Step 1: Push Your Code to GitHub

### 1.1 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `nutrisnap` or `food-recognition`
3. Description: `AI-powered food recognition and nutrition tracking app`
4. Choose **Public** (for free Render deployment)
5. Click **Create repository**

### 1.2 Set Up Git in Your Local Project
Open terminal in the project root and run:

```bash
cd /home/shivam/Downloads/Food-Image-Recognition-Final/Food-Image-Recognition
git init
git add .
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
git commit -m "Initial commit: NutriSnap Flask application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nutrisnap.git
git push -u origin main
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- Use HTTPS (username + personal access token) or SSH key

---

## Step 2: Deploy to Render.com

### 2.1 Connect GitHub to Render
1. Go to https://render.com
2. Sign up with GitHub (or create account)
3. Click **New +** → **Web Service**
4. Select your GitHub repo (`nutrisnap`)
5. Click **Connect**

### 2.2 Configure Render Settings
Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `nutrisnap` |
| **Environment** | `Python 3` |
| **Region** | Choose your region (closer = faster) |
| **Branch** | `main` |
| **Build Command** | (leave empty or use default) |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app` |

### 2.3 Environment Variables
Click **Environment** and add:

```
FLASK_ENV=production
SECRET_KEY=your-very-random-secret-key-here
```

To generate a strong SECRET_KEY, run in terminal:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2.4 Instance Type
- Choose **Free** (750 hours/month)

### 2.5 Deploy!
Click **Create Web Service** and wait ~2-3 minutes for deployment.

---

## Step 3: Your Live App

Once deployed, you'll get a URL like:
```
https://nutrisnap-xyz.onrender.com
```

✅ Your app is live! Share this link with friends.

---

## Important Notes

### Keeping Your App Running (Free Tier)
- Free tier apps sleep after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- To keep alive (upgrade to paid) or accept the sleep

### Database
- Currently uses SQLite (works on Render)
- If you want persistent database, use Render's free PostgreSQL:
  1. Create PostgreSQL database on Render (free tier available)
  2. Get connection string
  3. Set `DATABASE_URL` environment variable
  4. Update `config.py` to use PostgreSQL URI

### TensorFlow Model Notes
- Model (~100MB) loads on first request
- Takes ~20-30 seconds first time
- Cached afterwards
- If app sleeps, model reloads on next request

---

## Troubleshooting

### App stuck in building
- Check build logs in Render dashboard
- Ensure `requirements.txt` has all dependencies

### 500 Error
- Check logs in Render dashboard (Logs tab)
- Common issues:
  - `SECRET_KEY` not set
  - Wrong Python version
  - Missing environment variables

### App times out
- TensorFlow takes time on first load
- Render timeout is 120 seconds (should be enough)
- If persists, upgrade instance or optimize code

### Need faster performance?
- Upgrade to paid tier ($7/month minimum)
- Adds persistent storage
- Better CPU/RAM

---

## Optional: Use PostgreSQL on Render

### Create Free PostgreSQL Database
1. In Render dashboard, click **New +** → **PostgreSQL**
2. Name: `nutrisnap-db`
3. Choose **Free** tier
4. Create database
5. Copy connection string

### Update Your App
In Render Web Service settings, add environment variable:
```
DATABASE_URL=your_postgres_connection_string
```

Then on your local machine, update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///nutrisnap.db'
```

Push to GitHub:
```bash
git add config.py
git commit -m "Update database configuration"
git push
```

Render auto-deploys on push! 🚀

---

## Next Steps After Deployment

1. **Test your app** - Visit your Render URL
2. **Share the link** - Send to friends/team
3. **Monitor performance** - Check Render dashboard
4. **Set up custom domain** (optional) - In Render settings
5. **Enable auto-redeploy** - Settings → Auto-Deploy from GitHub

---

## Free Forever Options Summary

| Platform | Database | Always On (Free) | Cold Start |
|----------|----------|------------------|-----------|
| **Render** ⭐ | Yes (free tier) | 750h/month | 30s first |
| Vercel | No | No | Serverless |
| Railway | Yes (limited) | ~5h/month | 30s+ |
| Heroku | No | Killed | Paid only |

**Choice: Render is best for this Flask app** ✅

---

## Support
- Render docs: https://render.com/docs
- Flask deployment: https://flask.palletsprojects.com/deployment/
- Ask in Render dashboard live chat for help

Good luck! 🚀
