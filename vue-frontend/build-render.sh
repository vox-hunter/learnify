#!/bin/bash
# Build script for Render deployment
# Sets environment variables and builds the Vue frontend

cd vue-frontend
export VITE_API_URL=https://ai-loom-backend.onrender.com
npm install
npm run build
