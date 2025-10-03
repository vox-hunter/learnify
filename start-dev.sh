#!/bin/bash

# Learnify - Development Startup Script
# This script starts both the FastAPI backend and Vue.js frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Learnify Development Server Setup   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f "api/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: api/.env not found!${NC}"
    echo -e "Creating from api/.env.example..."
    if [ -f "api/.env.example" ]; then
        cp api/.env.example api/.env
        echo -e "${RED}Please edit api/.env with your API keys and MongoDB URI${NC}"
        echo -e "Then run this script again."
        exit 1
    else
        echo -e "${RED}Error: api/.env.example not found${NC}"
        exit 1
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Check MongoDB (optional warning)
if ! command -v mongod &> /dev/null; then
    echo -e "${YELLOW}⚠️  MongoDB not found locally. Make sure you're using MongoDB Atlas or have MongoDB running${NC}"
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Install backend dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
source venv/bin/activate
pip install -q -r api/requirements.txt

# Install frontend dependencies if needed
if [ ! -d "vue-frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd vue-frontend
    npm install
    cd ..
fi

echo ""
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    echo -e "${GREEN}✓ Servers stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}🚀 Starting FastAPI backend...${NC}"
cd api
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check api/.env configuration${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend running on http://localhost:8000${NC}"
echo -e "  API Docs: http://localhost:8000/docs"
echo ""

# Start frontend
echo -e "${BLUE}🚀 Starting Vue.js frontend...${NC}"
cd vue-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Check if frontend started
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend running on http://localhost:3000${NC}"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Learnify is ready!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop both servers"
echo ""

# Wait for user to stop
wait
