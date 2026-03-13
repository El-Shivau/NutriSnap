# 🚀 NutriSnap - Ready for Deployment!

## Current Status
✅ **App is running locally** on `http://127.0.0.1:5000`  
✅ **Production-ready configuration**  
✅ **Deployment files created**  

---

## Quick Deployment to Render (5 Minutes)

### Option A: Automatic Setup (Recommended)
```bash
cd /home/shivam/Downloads/Food-Image-Recognition-Final/Food-Image-Recognition
bash deploy.sh "Your Name" "your.email@gmail.com" "your-github-username"
```

Then:
1. Create repo on GitHub (https://github.com/new)
2. Run: `git push -u origin main`
3. Go to Render.com, connect GitHub, deploy

### Option B: Manual Setup
See `RENDER_DEPLOYMENT.md` for step-by-step instructions.

---

## Files for Deployment
✅ `wsgi.py` - Production entry point  
✅ `Procfile` - Render configuration  
✅ `requirements.txt` - Python dependencies  
✅ `.env.example` - Environment template  
✅ `deploy.sh` - Quick git setup script  
✅ `RENDER_DEPLOYMENT.md` - Full deployment guide  

---

## Why Render?
- ✅ **Free tier**: 750 hours/month = always-on single app
- ✅ **Perfect for Flask** with TensorFlow
- ✅ **No cold starts** (unlike serverless)
- ✅ **Free PostgreSQL** if you upgrade
- ✅ **GitHub integration** - auto-deploys on push
- ✅ **Simple UI** - easy to manage

---

## What You'll Get
After deployment:
- 🌐 Live app URL: `https://nutrisnap-xxx.onrender.com`
- 👥 Share link with anyone
- 📱 Works on phone + desktop
- 🚀 Auto-redeploys when you push to GitHub

---

## Important Notes

### TensorFlow on Render
- Model loads on first request (takes ~20-30 seconds)
- Then works instantly for subsequent requests
- If app sleeps, model reloads next time

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- Wakes up on next request (30s delay)
- 750 hours/month = 31 days of continuous running
- Enough for a single always-on app

### To Keep App Awake
-Upgrade to paid ($7+/month minimum) OR
- Accept sleep/wake behavior (totally fine for development)

---

## Deployment Checklist

- [ ] 1. Create GitHub account (if needed)
- [ ] 2. Create GitHub repository named `nutrisnap`
- [ ] 3. Run `bash deploy.sh` or manual git setup
- [ ] 4. Push code: `git push -u origin main`
- [ ] 5. Create Render account at render.com
- [ ] 6. Connect GitHub to Render
- [ ] 7. Create Web Service from your repo
- [ ] 8. Set start command: `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
- [ ] 9. Deploy!
- [ ] 10. Test your live app

---

## Next Commands

### 1. Quick Deploy (Automatic)
```bash
cd /home/shivam/Downloads/Food-Image-Recognition-Final/Food-Image-Recognition

# Run the deployment setup script
bash deploy.sh "Your Full Name" "your.email@gmail.com" "github-username"

# After creating the GitHub repo, push:
git push -u origin main
```

### 2. Create GitHub Repo
- Go to https://github.com/new
- Name: `nutrisnap`
- Make it **PUBLIC**
- Click Create

### 3. Deploy on Render
- Go to https://render.com
- Sign up with GitHub
- New Web Service → Select `nutrisnap` repo
- Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
- Deploy!

---

## Support Resources

| Resource | Link |
|----------|------|
| Render Docs | https://render.com/docs |
| Flask Deployment | https://flask.palletsprojects.com/deployment/ |
| GitHub Help | https://docs.github.com |
| Render Chat | Available in dashboard |

---

## Free Forever Comparison

| Service | Type | Database | Always On | Cost |
|---------|------|----------|-----------|------|
| **Render** ⭐ | PaaS | Yes (free) | 750h/month | Free |
| Vercel | Serverless | No | No | Free (limited) |
| Railway | PaaS | Yes | 5h/month | Free ($5 credit) |
| Heroku | PaaS | Yes | No | Paid only |

**Render wins for your use case!** 🎯

---

## Common Questions

**Q: Will my TensorFlow model work on Render?**  
A: Yes! Render supports large models. First load ~20-30s, then instant.

**Q: Can I use my own domain?**  
A: Yes! Render supports custom domains in settings (even on free tier).

**Q: What if app goes down?**  
A: Render has 99.99% uptime. Logs available in dashboard for debugging.

**Q: Can I upgrade later?**  
A: Yes! Start free, upgrade anytime. No data loss.

**Q: How do I update my app after deployment?**  
A: Just `git push` to GitHub - Render auto-deploys!

---

## You're All Set! 🎉

Your app is production-ready. Time to deploy and go live! 🚀

For questions: Check the deployment guide or Render documentation.

---

**Created:** March 14, 2026  
**App Status:** ✅ Running Locally | Ready for Cloud Deployment
