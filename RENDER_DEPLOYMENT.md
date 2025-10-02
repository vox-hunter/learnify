# Render Deployment Guide for Learnify

This guide provides complete instructions for deploying Learnify (Vue.js frontend + FastAPI backend) on Render web service.

## Architecture Overview

Learnify consists of two services:
- **Backend**: FastAPI application (Python) - Handles API requests, AI processing, authentication
- **Frontend**: Vue.js application (Static Site) - User interface

## Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account (free tier available)
3. A [Google AI API Key](https://makersuite.google.com/app/apikey) (Gemini API)
4. Git repository connected to Render

## Deployment Methods

### Method 1: Using render.yaml (Recommended)

This method uses the `render.yaml` file in the repository to configure both services automatically.

#### Steps:

1. **Fork or clone this repository** to your GitHub account

2. **Go to [Render Dashboard](https://dashboard.render.com/)**

3. **Click "New" → "Blueprint"**

4. **Connect your GitHub repository**

5. **Render will automatically detect the `render.yaml` file**

6. **Configure Environment Variables** for the backend service:
   - `GEMINI_API_KEY`: Your Google AI API key
   - `MONGODB_URI`: Your MongoDB connection string
   - `DEBUG_MODE`: `False` (already set in render.yaml)
   - `COOKIE_ENCRYPTION_KEY`: Auto-generated (already configured)

7. **Click "Apply"** to deploy both services

8. **Wait for deployment** (5-10 minutes for first deployment)

9. **Update Frontend API URL** (see Configuration section below)

### Method 2: Manual Deployment

#### Step 1: Deploy the Backend

1. **Go to Render Dashboard** → Click "New" → "Web Service"

2. **Connect your repository**

3. **Configure the service:**
   - **Name**: `learnify-backend`
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r api/requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

4. **Add Environment Variables:**
   - `GEMINI_API_KEY`: Your Google AI API key
   - `MONGODB_URI`: Your MongoDB connection string (e.g., `mongodb+srv://username:password@cluster.mongodb.net/learnify_auth?retryWrites=true&w=majority`)
   - `DEBUG_MODE`: `False`
   - `PYTHON_VERSION`: `3.11.0`

5. **Click "Create Web Service"**

6. **Wait for deployment** and note the backend URL (e.g., `https://learnify-backend.onrender.com`)

#### Step 2: Deploy the Frontend

1. **Go to Render Dashboard** → Click "New" → "Static Site"

2. **Connect the same repository**

3. **Configure the service:**
   - **Name**: `learnify-frontend`
   - **Region**: Oregon (or same as backend)
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**:
     ```bash
     cd vue-frontend && npm install && npm run build
     ```
   - **Publish Directory**: `vue-frontend/dist`

4. **Add Environment Variable** (during build):
   - `VITE_API_URL`: Your backend URL (e.g., `https://learnify-backend.onrender.com`)

5. **Configure Rewrites** (for API proxy):
   - Go to "Redirects/Rewrites" tab
   - Add rewrite rule:
     - **Source**: `/api/*`
     - **Destination**: `https://learnify-backend.onrender.com/api/*`
     - **Type**: Rewrite

6. **Click "Create Static Site"**

## Configuration

### Backend Configuration

The backend requires the following environment variables:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google AI API key for course generation | `AIzaSy...` | Yes |
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://...` | Yes |
| `DEBUG_MODE` | Enable debug logging | `False` | No (default: False) |
| `COOKIE_ENCRYPTION_KEY` | Key for cookie encryption | Auto-generated | No |

### Frontend Configuration

Update the API URL in the Vue frontend:

1. **Edit `vue-frontend/src/services/api.js`** or create a `.env` file:
   ```env
   VITE_API_URL=https://learnify-backend.onrender.com
   ```

2. **Or update the axios baseURL** in `vue-frontend/src/services/api.js`:
   ```javascript
   const API_URL = import.meta.env.VITE_API_URL || 'https://learnify-backend.onrender.com';
   ```

## Build Commands Reference

### Backend Build Command
```bash
pip install -r api/requirements.txt
```

**What it does:**
- Installs all Python dependencies including FastAPI, uvicorn, pymongo, etc.
- Takes ~2-3 minutes on first build

### Backend Start Command
```bash
cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**What it does:**
- Changes to the `api` directory
- Starts the FastAPI application using uvicorn
- Binds to all interfaces (0.0.0.0) and uses Render's assigned PORT

### Frontend Build Command
```bash
cd vue-frontend && npm install && npm run build
```

**What it does:**
- Changes to the `vue-frontend` directory
- Installs Node.js dependencies (Vue, Vite, axios, etc.)
- Builds the production-optimized Vue.js application
- Takes ~3-5 minutes on first build

### Frontend Publish Directory
```
vue-frontend/dist
```

**What it contains:**
- Compiled, minified, and optimized static files (HTML, CSS, JS)
- Ready to be served by Render's CDN

## Pre-Deploy Checklist

Before deploying, ensure you have:

- [ ] MongoDB Atlas cluster set up and connection string ready
- [ ] Google AI API key obtained from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Repository pushed to GitHub (or connected to Render)
- [ ] Reviewed and updated `api/.env.example` with your values (don't commit actual `.env`)
- [ ] Updated CORS origins in `api/main.py` if deploying to custom domain

## Post-Deployment

### Verify Backend Deployment

1. Visit your backend URL: `https://learnify-backend.onrender.com`
2. You should see: `{"message": "Learnify API", "version": "1.0.0", "status": "running"}`
3. Check health: `https://learnify-backend.onrender.com/health`
4. View API docs: `https://learnify-backend.onrender.com/docs`

### Verify Frontend Deployment

1. Visit your frontend URL: `https://learnify-frontend.onrender.com`
2. The Vue.js application should load
3. Test registration and login functionality
4. Try generating a course from a PDF

### Update CORS Settings

If you have a custom domain or the frontend URL is different, update CORS in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://learnify-frontend.onrender.com",  # Add your frontend URL
        "https://your-custom-domain.com"  # Add custom domain if any
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Backend Issues

**Issue**: Service won't start
- **Solution**: Check logs in Render dashboard
- Verify all environment variables are set correctly
- Ensure `MONGODB_URI` is accessible from Render's IP

**Issue**: "Authentication service unavailable"
- **Solution**: Check MongoDB connection
- Verify `MONGODB_URI` format and credentials
- Ensure MongoDB Atlas allows connections from anywhere (0.0.0.0/0) or Render's IPs

**Issue**: "GEMINI_API_KEY not found"
- **Solution**: Add the environment variable in Render dashboard
- Ensure there are no extra spaces or quotes in the key

### Frontend Issues

**Issue**: "Cannot connect to API"
- **Solution**: Verify backend is running and accessible
- Check that API URL is correctly configured
- Ensure rewrites/redirects are set up in Render

**Issue**: Blank page after deployment
- **Solution**: Check browser console for errors
- Verify build completed successfully
- Check that `vue-frontend/dist` was created and contains files

### Performance Issues

**Issue**: Slow cold starts (Free tier)
- **Solution**: Render's free tier spins down after inactivity
- Consider upgrading to a paid plan for always-on services
- First request after inactivity may take 30-60 seconds

## Monitoring

### Health Checks

- Backend health: `https://learnify-backend.onrender.com/health`
- Returns status of authentication and course manager services

### Logs

- Access logs through Render Dashboard → Select Service → Logs tab
- Backend logs show API requests, errors, and debugging info
- Frontend build logs show npm install and build process

## Scaling

### Free Tier Limitations

- Backend: 750 hours/month, spins down after inactivity
- Frontend: Unlimited bandwidth (100 GB/month)
- Both services spin down after 15 minutes of inactivity

### Upgrading

For production use, consider:
- **Starter Plan** ($7/month per service): Always-on, no spin down
- **Standard Plan** ($25/month per service): More resources, better performance

## Security Best Practices

1. **Never commit** `.env` files with real credentials
2. **Use strong passwords** for MongoDB
3. **Rotate API keys** periodically
4. **Enable MongoDB IP whitelist** when possible
5. **Use HTTPS only** (Render provides free SSL)
6. **Set secure cookie settings** in production

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)

## Support

For issues specific to this deployment:
1. Check Render logs for errors
2. Verify environment variables are set correctly
3. Test backend API directly using `/docs` endpoint
4. Open an issue on GitHub repository

## Quick Deploy Links

Once configured:
- **Backend**: [Deploy to Render](https://render.com/deploy)
- **Frontend**: Uses same repository, deployed as static site

---

**Last Updated**: 2025
**Deployment Platform**: Render.com
**Stack**: Vue.js 3 + FastAPI + MongoDB + Google Gemini AI
