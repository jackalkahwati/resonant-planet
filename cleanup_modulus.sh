#!/bin/bash
# Remove embedded Modulus code and configure API connection

set -e

echo "🧹 Cleaning up embedded Modulus code..."
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Remove the large modulus_real directory
if [ -d "backend/physics/modulus_real" ]; then
    echo "📦 Removing backend/physics/modulus_real/ (32MB)..."
    rm -rf backend/physics/modulus_real
    echo -e "${GREEN}✅ Removed embedded Modulus code${NC}"
else
    echo "⚠️  modulus_real/ not found (already removed?)"
fi

# Update .gitignore
if ! grep -q "modulus_real" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Modulus (use external API instead)" >> .gitignore
    echo "backend/physics/modulus_real/" >> .gitignore
    echo -e "${GREEN}✅ Updated .gitignore${NC}"
fi

# Remove deployment scripts that are no longer needed
rm -f deploy_modulus_to_cloudrun.sh
rm -f CLOUDRUN_QUICK_START.md
echo -e "${GREEN}✅ Removed local Modulus deployment scripts${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ CLEANUP COMPLETE!                                     ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""
echo -e "${YELLOW}📝 NEXT STEPS:${NC}"
echo ""
echo "1. Set your Modulus Cloud Run URL:"
echo "   Edit backend/.env and add:"
echo "   "
echo "   USE_MODULUS_API=true"
echo "   MODULUS_API_URL=https://your-modulus-xxx.run.app"
echo ""
echo "2. Test the connection:"
echo "   cd backend"
echo "   python -c \"from physics import get_backend_info; print(get_backend_info())\""
echo ""
echo "3. Update Railway environment variables:"
echo "   Railway Dashboard → Variables → Add:"
echo "   - USE_MODULUS_API=true"
echo "   - MODULUS_API_URL=https://your-modulus-xxx.run.app"
echo ""
echo "4. Commit and push:"
echo "   git add ."
echo "   git commit -m \"Remove embedded Modulus code, use external API\""
echo "   git push origin main"
echo ""
echo "📚 See CONNECT_TO_MODULUS.md for full documentation"
echo ""
echo -e "${GREEN}Your repo will be ~32MB smaller!${NC} 🎉"
