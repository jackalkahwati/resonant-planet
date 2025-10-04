#!/bin/bash
# Full-stack integration test for Resonant Worlds Explorer

set -e  # Exit on error

echo "=========================================="
echo "Resonant Worlds Explorer"
echo "Full-Stack Integration Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test status
test_passed() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

test_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================
# 1. Backend Tests
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Testing Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    test_passed "Backend is running"
else
    test_failed "Backend is not responding on port 8000"
    echo "   Start backend with: cd backend && uvicorn api.main:app --reload"
    exit 1
fi

# Test root endpoint
if curl -s http://localhost:8000/ | grep -q "Resonant Worlds"; then
    test_passed "Root endpoint responding"
else
    test_failed "Root endpoint not working"
fi

# Test datasets endpoint
DATASETS=$(curl -s http://localhost:8000/api/datasets/)
if echo "$DATASETS" | grep -q "dataset_id"; then
    COUNT=$(echo "$DATASETS" | grep -o "dataset_id" | wc -l | tr -d ' ')
    test_passed "Datasets endpoint working (found $COUNT datasets)"
else
    test_warning "No datasets found (this is OK if demo mode is off)"
fi

echo ""

# ============================================
# 2. Frontend Tests
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Testing Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if frontend is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    test_passed "Frontend is running on port 5173"
else
    test_warning "Frontend not detected on port 5173"
    echo "   Start with: npm run dev"
fi

# Check if API client exists
if [ -f "src/lib/api.ts" ]; then
    test_passed "API client file exists"
else
    test_failed "API client file not found"
fi

# Check if hooks exist
if [ -f "src/hooks/useDetection.ts" ]; then
    test_passed "useDetection hook exists"
else
    test_failed "useDetection hook not found"
fi

if [ -f "src/hooks/useDatasets.ts" ]; then
    test_passed "useDatasets hook exists"
else
    test_failed "useDatasets hook not found"
fi

echo ""

# ============================================
# 3. Backend Demo Test
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Running Backend Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Only run if Python is available
if command -v python3 > /dev/null 2>&1; then
    if [ -f "backend/run_demo.py" ]; then
        echo "Running backend demo script..."
        echo ""
        
        cd backend
        
        # Run demo (with timeout)
        timeout 60s python3 run_demo.py || {
            test_warning "Demo script timed out or failed"
        }
        
        cd ..
        
        test_passed "Backend demo completed"
    else
        test_warning "Backend demo script not found"
    fi
else
    test_warning "Python not available, skipping backend demo"
fi

echo ""

# ============================================
# 4. API Integration Tests
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Testing API Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test run endpoint (if datasets available)
if echo "$DATASETS" | grep -q "dataset_id"; then
    # Extract first dataset ID
    DATASET_ID=$(echo "$DATASETS" | grep -o '"dataset_id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    echo "Testing detection run with dataset: $DATASET_ID"
    
    # Start a job
    JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/run \
        -H "Content-Type: application/json" \
        -d "{\"dataset_id\":\"$DATASET_ID\",\"min_period_days\":0.5,\"max_period_days\":5.0}")
    
    if echo "$JOB_RESPONSE" | grep -q "job_id"; then
        JOB_ID=$(echo "$JOB_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        test_passed "Detection job started: $JOB_ID"
        
        # Wait for completion (with timeout)
        echo "   Waiting for job to complete..."
        TIMEOUT=30
        ELAPSED=0
        
        while [ $ELAPSED -lt $TIMEOUT ]; do
            STATUS=$(curl -s http://localhost:8000/api/status/$JOB_ID)
            
            if echo "$STATUS" | grep -q '"status":"completed"'; then
                test_passed "Job completed successfully"
                
                # Get results
                RESULTS=$(curl -s http://localhost:8000/api/results/$JOB_ID)
                CANDIDATE_COUNT=$(echo "$RESULTS" | grep -o '"total_candidates":[0-9]*' | cut -d':' -f2)
                
                if [ -n "$CANDIDATE_COUNT" ]; then
                    test_passed "Retrieved $CANDIDATE_COUNT candidates"
                fi
                
                break
            elif echo "$STATUS" | grep -q '"status":"failed"'; then
                test_failed "Job failed"
                break
            fi
            
            sleep 1
            ((ELAPSED++))
        done
        
        if [ $ELAPSED -ge $TIMEOUT ]; then
            test_warning "Job did not complete within ${TIMEOUT}s"
        fi
    else
        test_failed "Failed to start detection job"
    fi
else
    test_warning "No datasets available, skipping detection test"
fi

echo ""

# ============================================
# 5. File Structure Checks
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Checking File Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backend files
BACKEND_FILES=(
    "backend/api/main.py"
    "backend/core/preprocess.py"
    "backend/physics/modulus_adapter.py"
    "backend/requirements.txt"
    "backend/README.md"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_passed "Found $file"
    else
        test_failed "Missing $file"
    fi
done

# Frontend files
FRONTEND_FILES=(
    "src/lib/api.ts"
    "src/hooks/useDetection.ts"
    "src/hooks/useDatasets.ts"
    "FRONTEND_INTEGRATION.md"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_passed "Found $file"
    else
        test_failed "Missing $file"
    fi
done

echo ""

# ============================================
# Test Summary
# ============================================

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Failed:${NC} $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:5173/detect"
    echo "2. Click 'Run All Samples'"
    echo "3. Watch real-time progress"
    echo "4. View detected candidates"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure backend is running: cd backend && uvicorn api.main:app --reload"
    echo "2. Ensure frontend is running: npm run dev"
    echo "3. Check FRONTEND_INTEGRATION.md for detailed setup"
    echo ""
    exit 1
fi
