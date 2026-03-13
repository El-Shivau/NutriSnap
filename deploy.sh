#!/bin/bash
# Quick deployment script to GitHub and Render
# Usage: bash deploy.sh "Your Name" "your.email@gmail.com" "your-github-username"

if [ "$#" -ne 3 ]; then
    echo "Usage: bash deploy.sh \"Your Name\" \"your.email@gmail.com\" \"your-github-username\""
    echo ""
    echo "Example:"
    echo "  bash deploy.sh \"Shivam\" \"shivam@example.com\" \"shivamuser\""
    exit 1
fi

NAME=$1
EMAIL=$2
GITHUB_USER=$3
REPO_NAME="nutrisnap"

echo "═══════════════════════════════════════════════════"
echo "🚀 NutriSnap Deployment to Render"
echo "═══════════════════════════════════════════════════"
echo ""
echo "👤 Name: $NAME"
echo "📧 Email: $EMAIL"
echo "🐙 GitHub: $GITHUB_USER"
echo ""

# Step 1: Initialize git
echo "Step 1️⃣  Initializing Git repository..."
git init
git config user.name "$NAME"
git config user.email "$EMAIL"

# Step 2: Add all files
echo "Step 2️⃣  Adding files..."
git add .

# Step 3: Create initial commit
echo "Step 3️⃣  Creating initial commit..."
git commit -m "Initial commit: NutriSnap Flask application with ML"

# Step 4: Rename branch to main
echo "Step 4️⃣  Setting up main branch..."
git branch -M main

# Step 5: Add remote
echo "Step 5️⃣  Adding GitHub remote..."
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
git remote add origin "$REPO_URL"

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Git Setup Complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Create a repository on GitHub:"
echo "   → Go to https://github.com/new"
echo "   → Name: $REPO_NAME"
echo "   → Make it PUBLIC"
echo "   → Click 'Create repository'"
echo ""
echo "2️⃣  Push your code:"
echo "   → Run: git push -u origin main"
echo "   → (You may need to authenticate with GitHub)"
echo ""
echo "3️⃣  Deploy to Render:"
echo "   → Go to https://render.com"
echo "   → Sign up with GitHub"
echo "   → Click 'New +' → 'Web Service'"
echo "   → Select your repository"
echo "   → Start command: gunicorn -w 4 -b 0.0.0.0:\$PORT wsgi:app"
echo "   → Deploy!"
echo ""
echo "📚 For detailed instructions, see RENDER_DEPLOYMENT.md"
echo ""
