# Render Deployment Guide

## Services

### Backend (Web Service)
- **Service Name**: AI Loom backend
- **Service ID**: srv-d3ev7sffte5s73bdkru0
- **URL**: https://ai-loom-backend.onrender.com
- **Type**: Web Service (Python)
- **Build Command**: `pip install -r api/requirements.txt`
- **Start Command**: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Branch**: alpha

### Frontend (Static Site)
- **Service Name**: AI Loom Frontend
- **Service ID**: srv-d3ev937fte5s73bdm1s0
- **URL**: https://ai-loom-frontend.onrender.com
- **Type**: Static Site
- **Build Command**: `cd vue-frontend && VITE_API_URL=https://ai-loom-backend.onrender.com npm install && npm run build`
- **Publish Path**: `vue-frontend/dist`
- **Branch**: alpha

## Environment Variables

### Frontend (Static Site)
Set in build command:
- `VITE_API_URL`: `https://ai-loom-backend.onrender.com`

### Backend (Web Service)
MongoDB connection strings should be set in Render dashboard under Environment Variables.

## Manual Deployment Steps

### Update Frontend Build Command
1. Go to https://dashboard.render.com/static/srv-d3ev937fte5s73bdm1s0/settings
2. Update Build Command to:
   ```bash
   cd vue-frontend && VITE_API_URL=https://ai-loom-backend.onrender.com npm install && npm run build
   ```
3. Save and trigger manual deploy

### Backend is Ready
The backend already has CORS configured for the production frontend URL.

## Testing
- Backend health: https://ai-loom-backend.onrender.com/health
- Backend docs: https://ai-loom-backend.onrender.com/docs
- Frontend: https://ai-loom-frontend.onrender.com

## Recent Changes
1. Updated `api.js` to use `VITE_API_URL` environment variable
2. Added CORS origin for production frontend in `api/main.py`
3. Created build script with environment variables

## CORS Configuration
Backend now allows requests from:
- http://localhost:3000 (dev)
- http://localhost:8080 (dev)
- http://localhost:5173 (dev)
- https://ai-loom-frontend.onrender.com (production)
