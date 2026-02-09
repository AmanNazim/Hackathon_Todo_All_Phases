#!/bin/bash

# Deployment Helper Script
# Generates secrets and provides deployment commands

echo "🚀 Todo App Deployment Helper"
echo "=============================="
echo ""

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo "⚠️  openssl not found. Please install it to generate secrets."
    exit 1
fi

# Generate secrets
echo "📝 Generating Secrets..."
echo ""

JWT_SECRET=$(openssl rand -base64 32)
BETTER_AUTH_SECRET=$(openssl rand -base64 32)

echo "✅ Secrets Generated!"
echo ""
echo "Copy these to your deployment platforms:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "JWT_SECRET=$JWT_SECRET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save to file
cat > .deployment-secrets.txt << EOF
# Generated Secrets - $(date)
# ⚠️  KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

JWT_SECRET=$JWT_SECRET
BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET

# Add these to:
# - Railway: Variables tab
# - Vercel: Settings → Environment Variables
EOF

echo "💾 Secrets saved to: .deployment-secrets.txt"
echo "⚠️  Keep this file secure and DO NOT commit to git!"
echo ""

# Deployment URLs
echo "📋 Deployment Checklist:"
echo ""
echo "1️⃣  Database (Neon):"
echo "   → https://neon.tech"
echo "   → Create project and copy connection string"
echo ""
echo "2️⃣  Backend (Railway):"
echo "   → https://railway.app"
echo "   → Deploy from GitHub"
echo "   → Add environment variables (use secrets above)"
echo ""
echo "3️⃣  Frontend (Vercel):"
echo "   → https://vercel.com"
echo "   → Deploy from GitHub"
echo "   → Add NEXT_PUBLIC_API_URL with Railway URL"
echo ""

# Git check
if [ -d .git ]; then
    echo "✅ Git repository detected"

    # Check if there are uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo "⚠️  You have uncommitted changes"
        echo ""
        echo "Run these commands to commit and push:"
        echo "  git add ."
        echo "  git commit -m 'Prepare for deployment'"
        echo "  git push origin main"
    else
        echo "✅ No uncommitted changes"
    fi
else
    echo "⚠️  Not a git repository"
    echo ""
    echo "Initialize git with:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    echo "  git remote add origin <your-github-repo-url>"
    echo "  git push -u origin main"
fi

echo ""
echo "📖 For detailed instructions, see:"
echo "   → DEPLOYMENT_GUIDE.md"
echo "   → DEPLOYMENT_CHECKLIST.md"
echo ""
echo "🎉 Ready to deploy!"
