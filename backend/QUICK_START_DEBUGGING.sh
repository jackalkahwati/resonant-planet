#!/bin/bash
# Quick Start: Modulus Biosignature Debugging
# Run this when you're ready to identify the problem datasets

set -e

cd "$(dirname "$0")"

echo "=============================================="
echo "🧬 Modulus Biosignature Debug Pipeline"
echo "=============================================="
echo ""

# Check Modulus health
echo "1️⃣  Checking Modulus API health..."
if curl -s http://localhost:8000/v2/health | grep -q "healthy"; then
    echo "   ✅ Modulus is healthy"
else
    echo "   ❌ Modulus is not responding!"
    echo "   Start it with: cd backend/physics/modulus_real/api && python v2_api.py"
    exit 1
fi
echo ""

# Count datasets
echo "2️⃣  Dataset inventory..."
total=$(find assets/spectra -name "*.csv" 2>/dev/null | wc -l)
published=$(find assets/spectra/published_real -name "*.csv" 2>/dev/null | wc -l)
jwst=$(find assets/spectra/jwst_real -name "*.csv" 2>/dev/null | wc -l)
kepler=$(find assets/spectra/kepler -name "*.csv" 2>/dev/null | wc -l)

echo "   Total datasets: $total"
echo "   Published real: $published"
echo "   JWST real: $jwst"
echo "   Kepler: $kepler"
echo ""

# Run targeted scans
echo "3️⃣  Running targeted scans..."
echo ""

# Published real (highest priority)
if [ $published -gt 0 ]; then
    echo "   📊 Scanning published real JWST data..."
    PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/published_real \
        --timeout 90 \
        --retries 2 \
        --output scan_published_real.json \
        2>&1 | tee scan_published_real.log
    echo ""
fi

# JWST real
if [ $jwst -gt 0 ]; then
    echo "   📊 Scanning JWST real observations..."
    PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/jwst_real \
        --timeout 90 \
        --retries 2 \
        --output scan_jwst_real.json \
        2>&1 | tee scan_jwst_real.log
    echo ""
fi

# Kepler candidates
if [ $kepler -gt 0 ]; then
    echo "   📊 Scanning Kepler candidates..."
    PYTHONPATH=$(pwd) python scripts/debug_batch_scan.py assets/spectra/kepler \
        --timeout 90 \
        --retries 2 \
        --output scan_kepler.json \
        2>&1 | tee scan_kepler.log
    echo ""
fi

echo "=============================================="
echo "✅ Targeted scans complete!"
echo "=============================================="
echo ""
echo "Results saved to:"
echo "  - scan_published_real.json"
echo "  - scan_jwst_real.json"
echo "  - scan_kepler.json"
echo ""
echo "Next step: Check for any errors in the JSON files"
echo ""
echo "To run FULL scan on all datasets:"
echo "  PYTHONPATH=\$(pwd) python scripts/debug_batch_scan.py assets/spectra \\"
echo "      --timeout 120 --retries 3 --output full_scan.json"
echo ""


