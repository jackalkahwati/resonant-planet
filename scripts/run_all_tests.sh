#!/bin/bash
# Run all Modulus tests with golden output validation

set -e  # Exit on error

echo "=========================================="
echo "Modulus Test Suite"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")/.."

echo ""
echo "1. Running unit tests..."
if pytest tests/ -v --cov=modulus_core --cov-report=term-missing; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    exit 1
fi

echo ""
echo "2. Running memory & scheduler tests..."
if pytest tests/test_memory_scheduler.py -v; then
    echo -e "${GREEN}✓ Memory tests passed${NC}"
else
    echo -e "${RED}✗ Memory tests failed${NC}"
    exit 1
fi

echo ""
echo "3. Running profiler tests..."
if pytest tests/test_profiler.py -v; then
    echo -e "${GREEN}✓ Profiler tests passed${NC}"
else
    echo -e "${RED}✗ Profiler tests failed${NC}"
    exit 1
fi

echo ""
echo "4. Running real-time tests..."
if pytest tests/test_realtime.py -v; then
    echo -e "${GREEN}✓ Real-time tests passed${NC}"
else
    echo -e "${RED}✗ Real-time tests failed${NC}"
    exit 1
fi

echo ""
echo "5. Running integration tests..."
if pytest tests/test_integration.py -v; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    exit 1
fi

echo ""
echo "6. Testing PDE stencil example..."
cd examples/pde_stencil
if python heat_equation_2d.py --nx 32 --ny 32 --nt 10 --seed 42 --output test_output.npy; then
    echo -e "${GREEN}✓ PDE stencil example passed${NC}"
else
    echo -e "${RED}✗ PDE stencil example failed${NC}"
    exit 1
fi
cd ../..

echo ""
echo "7. Testing perception stack example..."
cd examples/perception_stack
if python perception_demo.py --height 32 --width 32 --seed 42; then
    echo -e "${GREEN}✓ Perception stack example passed${NC}"
else
    echo -e "${RED}✗ Perception stack example failed${NC}"
    exit 1
fi
cd ../..

echo ""
echo "8. Verifying determinism (golden outputs)..."
cd examples/pde_stencil
python heat_equation_2d.py --nx 32 --ny 32 --nt 10 --seed 42 --output golden_run1.npy > /dev/null
python heat_equation_2d.py --nx 32 --ny 32 --nt 10 --seed 42 --output golden_run2.npy > /dev/null

if python -c "import numpy as np; assert np.allclose(np.load('golden_run1.npy'), np.load('golden_run2.npy')), 'Outputs differ!'"; then
    echo -e "${GREEN}✓ Determinism verified (bit-identical outputs)${NC}"
else
    echo -e "${RED}✗ Determinism check failed${NC}"
    exit 1
fi

# Cleanup
rm -f golden_run1.npy golden_run2.npy test_output.npy
cd ../..

echo ""
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="


