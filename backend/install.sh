#!/bin/bash
# Installation script for Resonant Worlds Explorer Backend

set -e  # Exit on error

echo "=================================="
echo "Resonant Worlds Explorer Backend"
echo "Installation Script"
echo "=================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

# Check if we have Python 3.11+
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo "   ⚠️  Python 3.11+ required, found $PYTHON_VERSION"
    echo "   Please upgrade Python and try again"
    exit 1
fi

echo "   ✓ Python version OK"
echo ""

# Create virtual environment (optional but recommended)
echo "2. Setting up virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✓ Created virtual environment"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

echo "   ✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "3. Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip upgraded"
echo ""

# Install dependencies
echo "4. Installing dependencies..."
echo "   This may take 2-3 minutes..."
pip install -r requirements.txt > /dev/null 2>&1 || {
    echo "   ⚠️  Some dependencies failed to install"
    echo "   Trying again with verbose output..."
    pip install -r requirements.txt
}
echo "   ✓ Dependencies installed"
echo ""

# Create necessary directories
echo "5. Creating directories..."
mkdir -p uploads run_artifacts assets/demos assets/weights assets/models docs
echo "   ✓ Directories created"
echo ""

# Create .env file if it doesn't exist
echo "6. Setting up environment..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Backend configuration
HOST=0.0.0.0
PORT=8000

# Modulus integration
USE_LOCAL_MODULUS=true

# Demo and data
DEMO_MODE=true

# Job execution
JOB_BACKEND=background

# Logging
LOG_LEVEL=INFO
EOF
    echo "   ✓ Created .env file"
else
    echo "   .env file already exists"
fi
echo ""

# Test imports
echo "7. Testing installation..."
python3 -c "
import fastapi
import uvicorn
import numpy
import scipy
print('   ✓ Core packages installed correctly')
"
echo ""

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the server:"
echo "   $ source venv/bin/activate  # If not already activated"
echo "   $ uvicorn api.main:app --reload --port 8000"
echo ""
echo "2. In another terminal, run the demo:"
echo "   $ source venv/bin/activate"
echo "   $ python run_demo.py"
echo ""
echo "3. Or view API docs at:"
echo "   http://localhost:8000/docs"
echo ""
echo "Happy planet hunting! 🪐"
echo ""
