#!/bin/bash
# Fix Vercel deployment - ensure it deploys from main branch
# This script will trigger a fresh deployment from the correct branch

set -e

echo "🔧 Fixing Vercel Deployment Configuration"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ Not on main branch! Currently on: $CURRENT_BRANCH${NC}"
    echo "Switching to main branch..."
    git checkout main
fi

echo -e "${GREEN}✅ On main branch${NC}"
echo ""

# Get latest commit
LATEST_COMMIT=$(git rev-parse HEAD)
LATEST_COMMIT_SHORT=$(git rev-parse --short HEAD)
echo "Latest commit: $LATEST_COMMIT_SHORT - $(git log -1 --pretty=%B | head -1)"
echo ""

# Push to ensure GitHub is up to date
echo "📤 Ensuring GitHub is up to date..."
git push origin main
echo -e "${GREEN}✅ GitHub updated${NC}"
echo ""

# Trigger Vercel deployment from main
echo "🚀 Triggering Vercel deployment from main branch..."
echo ""
echo "Method 1: Using Git hook"
echo "Creating empty commit to trigger deployment..."
git commit --allow-empty -m "chore: trigger Vercel deployment from main [skip ci]"
git push origin main

echo ""
echo -e "${GREEN}✅ Deployment triggered!${NC}"
echo ""
echo "📊 Deployment Status:"
echo "===================="
echo ""
echo "1. Vercel: https://vercel.com/jackalkahwatis-projects/resonant-planet"
echo "   - Check 'Deployments' tab for progress"
echo "   - Should deploy from main branch now"
echo ""
echo "2. Railway: https://railway.app"
echo "   - Check 'resonant-worlds-backend' project"
echo "   - Deployment in progress"
echo ""
echo "⏱️  Expected completion time: 2-3 minutes"
echo ""
echo "🔗 Live URLs (after deployment):"
echo "   Frontend: https://resonant-planet.vercel.app"
echo "   Backend:  https://backend-api-production-6a91.up.railway.app"
echo ""
echo "✅ Done! Wait 2-3 minutes then test the live site."
