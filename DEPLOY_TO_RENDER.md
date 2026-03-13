# Deploy NutriSnap to Render.com ✅

## Step 1: Verify GitHub Push Completed
Wait for your code push to GitHub to complete (in progress). You can verify at:
```
https://github.com/El-Shivau/NutriSnap
```

---

## Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Click **Sign up**
3. Choose "Sign up with GitHub"
4. Authorize Render to access your GitHub account
5. You'll be logged in with your GitHub account (El-Shivau)

---

## Step 3: Deploy to Render

### 3A. Create New Web Service
1. Click **+ New** button (top-right)
2. Select **Web Service**
3. In "Connect a repository" section:
   - Search for "NutriSnap"
   - Select **El-Shivau/NutriSnap**
   - Click **Connect**

### 3B. Configure Web Service
Fill in the deployment settings:

| Field | Value |
|-------|-------|
| **Name** | `nutrisnap` |
| **Environment** | Python 3 |
| **Region** | (Choose closest to you) |
| **Branch** | `master` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app` |

### 3C. Add Environment Variables
1. Scroll down to **Environment**
2. Click **Add Environment Variable** and set:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a random string: `python -c "import os; print(os.urandom(16).hex())"` |

**Optional** (keep defaults):
- `DATABASE_URL`: Leave blank (uses SQLite)
- `USDA_API_KEY`: Leave as `DEMO_KEY`

### 3D: Select Plan & Deploy
1. Scroll to bottom
2. Choose **Free** plan
3. Click **Create Web Service**

Render will:
- ✅ Clone your repo
- ✅ Install dependencies (tensorflow, keras, flask, etc.)
- ✅ Build the app
- ✅ Deploy & start the app

---

## Step 4: Monitor Deployment
1. You'll see a **Build & Deploy** log
2. Wait for: `=== Build successful`
3. Then: `Listening on 0.0.0.0:PORT`

Your app URL will be: `https://nutrisnap-xxxxx.onrender.com`

---

## Step 5: Test Your Live App
1. Click on the **Service URL** (shows at top)
2. You should see the NutriSnap landing page
3. Register a new account
4. Test all features:
   - Register/Login ✅
   - Scan food images ✅
   - Add food logs ✅
   - View dashboard ✅
   - Find friends ✅
   - Use leaderboard ✅

---

## Troubleshooting

### "Free tier exhausted" error?
- Render offers 750 free hours/month (free tier)
- This is enough for: 750h ÷ 720h/month = 1 always-on app
- For continuous running, upgrade to Starter plan ($7/month)

### App shows 502 Bad Gateway?
1. Check **Logs** tab
2. Look for errors
3. Common causes:
   - Missing dependencies → run build again
   - Database issue → check SQLite file permissions
   - Port binding issue → check Procfile has `$PORT`

### App loads slowly?
- TensorFlow model takes ~5-10 seconds on first load
- This is normal (model is 300MB+)
- Second image scans are faster (model cached)

### Need to update code?
1. Git push changes to GitHub
2. Render auto-redeploys on push
3. Check **Deployments** tab to see status

---

## Environment Variables Explained

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_ENV` | Production mode vs Debug | `production` |
| `SECRET_KEY` | Session encryption key | Generated |
| `DATABASE_URL` | Database connection string | Use SQLite locally |
| `USDA_API_KEY` | Nutrition database API key | `DEMO_KEY` (limited) |

---

## Optional: Use PostgreSQL on Render

If you want a remote database instead of SQLite:

1. In Render dashboard, create **PostgreSQL** database
2. Copy connection string
3. Add env var: `DATABASE_URL` = [postgres-connection-string]
4. Git push to redeploy

**Warning**: TensorFlow + PostgreSQL drivers may cause memory issues on free tier. SQLite is recommended.

---

## Next Steps After Deployment ✅

- Share your app URL: `https://nutrisnap-xxxxx.onrender.com`
- Invite friends to register
- Upload photos and build nutrition logs
- Climb the leaderboard!

**Created**: March 14, 2026
**Status**: ✅ Ready for Render deployment
