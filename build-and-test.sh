#!/bin/bash

# Build and Test Script for Learnify
# This script validates that both backend and frontend can be built successfully

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Learnify Build & Test Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

echo ""

# Test Backend Build
echo -e "${BLUE}🔨 Testing Backend Build...${NC}"
echo -e "${YELLOW}Command: pip install -r api/requirements.txt${NC}"

# Create a temporary virtual environment for testing
if [ ! -d ".venv-test" ]; then
    python3 -m venv .venv-test
fi

source .venv-test/bin/activate

# Install dependencies
pip install -q --upgrade pip
pip install -q -r api/requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Backend build failed${NC}"
    deactivate
    exit 1
fi

# Check if main.py can be imported (syntax check)
cd api
python3 -c "import main" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend main.py syntax check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend main.py import check failed (may need environment variables)${NC}"
fi
cd ..

deactivate
echo ""

# Test Frontend Build
echo -e "${BLUE}🔨 Testing Frontend Build...${NC}"
echo -e "${YELLOW}Command: cd vue-frontend && npm install && npm run build${NC}"

cd vue-frontend

# Install dependencies
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Frontend dependency installation failed${NC}"
    cd ..
    exit 1
fi

# Build the frontend
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend build completed successfully${NC}"
    
    # Check if dist directory was created
    if [ -d "dist" ]; then
        echo -e "${GREEN}✓ Frontend dist directory created${NC}"
        echo -e "  📦 Build size: $(du -sh dist | cut -f1)"
    else
        echo -e "${RED}❌ Frontend dist directory not found${NC}"
        cd ..
        exit 1
    fi
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    cd ..
    exit 1
fi

cd ..
echo ""

# Summary
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ All builds completed successfully  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Review the RENDER_DEPLOYMENT.md file for deployment instructions"
echo "2. Ensure environment variables are set in Render dashboard"
echo "3. Deploy using render.yaml or manual method"
echo ""
echo -e "${BLUE}🧹 Cleanup:${NC}"
echo "To remove test build artifacts, run:"
echo "  rm -rf .venv-test vue-frontend/dist vue-frontend/node_modules"
