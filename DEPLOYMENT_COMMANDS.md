# Deployment Commands Quick Reference

This is a quick reference card for Render deployment commands and configuration.

## 🚀 Render Configuration Summary

### Backend Service (FastAPI)

**Service Type**: Web Service  
**Environment**: Python 3  
**Plan**: Free (or Starter/Standard)

#### Build Command
```bash
pip install -r api/requirements.txt
```

#### Start Command
```bash
cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Pre-Deploy Command
```bash
# Optional: Run tests before deployment
# python -m pytest api/tests/
```

#### Environment Variables (Required)
```bash
GEMINI_API_KEY=your_google_ai_api_key
MONGODB_URI=your_mongodb_connection_string
DEBUG_MODE=False
PYTHON_VERSION=3.11.0
```

---

### Frontend Service (Vue.js Static Site)

**Service Type**: Static Site  
**Environment**: Static  
**Plan**: Free (or Starter/Standard)

#### Build Command
```bash
cd vue-frontend && npm install && npm run build
```

#### Publish Directory
```
vue-frontend/dist
```

#### Pre-Deploy Command
```bash
# Optional: Run linting and tests
# cd vue-frontend && npm run lint && npm run test
```

#### Environment Variables (Build Time)
```bash
VITE_API_URL=https://learnify-backend.onrender.com
```

---

## 📋 Local Build & Test Commands

### Test Backend Build
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Run the backend
cd api && uvicorn main:app --reload
```

### Test Frontend Build
```bash
# Install dependencies
cd vue-frontend && npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Test Both Services
```bash
# Run the build and test script
./build-and-test.sh
```

---

## 🔧 Configuration Files

### render.yaml
Location: `./render.yaml`  
Purpose: Automated deployment configuration for both services

### Backend .env
Location: `api/.env` (create from `api/.env.example`)  
Purpose: Backend environment variables for local development

### Frontend .env
Location: `vue-frontend/.env.production`  
Purpose: Frontend environment variables for production build

---

## 📦 Dependencies

### Backend Dependencies
- **File**: `api/requirements.txt`
- **Key Packages**: FastAPI, uvicorn, pymongo, google-genai, pydantic
- **Install Time**: ~2-3 minutes

### Frontend Dependencies
- **File**: `vue-frontend/package.json`
- **Key Packages**: Vue 3, Vite, Vue Router, Pinia, Axios
- **Install Time**: ~3-5 minutes

---

## 🔄 Deployment Workflow

### Using render.yaml (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **In Render Dashboard**
   - Click "New" → "Blueprint"
   - Select your repository
   - Add environment variables
   - Click "Apply"

3. **Render will automatically**
   - Read `render.yaml`
   - Create both services
   - Run build commands
   - Deploy applications

### Manual Deployment

1. **Deploy Backend**
   - New → Web Service
   - Connect repository
   - Set build/start commands (see above)
   - Add environment variables
   - Deploy

2. **Deploy Frontend**
   - New → Static Site
   - Connect repository
   - Set build command and publish directory (see above)
   - Add API rewrite rules
   - Deploy

---

## 🧪 Testing Deployment

### Backend Health Check
```bash
curl https://learnify-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "auth_available": true,
  "course_manager_available": true
}
```

### Frontend Access
```bash
curl -I https://learnify-frontend.onrender.com
```

Expected: HTTP 200 OK

### API Documentation
Visit: `https://learnify-backend.onrender.com/docs`

---

## 🐛 Common Issues & Fixes

### Issue: Build fails for backend
**Solution**: Check Python version and requirements.txt syntax
```bash
# Locally test
pip install -r api/requirements.txt
```

### Issue: Frontend build fails
**Solution**: Check Node version and package.json
```bash
# Locally test
cd vue-frontend && npm install && npm run build
```

### Issue: Can't connect to MongoDB
**Solution**: Check MongoDB URI and whitelist Render IPs
- MongoDB Atlas → Network Access → Add 0.0.0.0/0

### Issue: CORS errors
**Solution**: Update CORS origins in `api/main.py`
```python
allow_origins=[
    "https://learnify-frontend.onrender.com",
    "https://your-domain.com"
]
```

---

## 📊 Build Time Estimates

| Step | Duration | Notes |
|------|----------|-------|
| Backend: Install Dependencies | 2-3 min | First build only |
| Backend: Startup | 10-30 sec | Subsequent deploys |
| Frontend: Install Dependencies | 3-5 min | First build only |
| Frontend: Build | 1-2 min | Every deploy |
| Total First Deploy | ~8-10 min | One-time |
| Total Subsequent Deploys | ~3-5 min | Cached deps |

---

## 🔐 Security Checklist

- [ ] Environment variables set in Render (not in code)
- [ ] `.env` files in `.gitignore`
- [ ] MongoDB IP whitelist configured
- [ ] CORS origins restricted to your domains
- [ ] HTTPS enabled (automatic on Render)
- [ ] Strong passwords for MongoDB
- [ ] API keys rotated periodically

---

## 📚 Additional Resources

- **Full Guide**: See `RENDER_DEPLOYMENT.md`
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Vue Docs**: https://vuejs.org/

---

## 🆘 Quick Support

1. **Check Logs**: Render Dashboard → Service → Logs
2. **Test Locally**: Run `./build-and-test.sh`
3. **Verify Env Vars**: Render Dashboard → Service → Environment
4. **Check Status**: Visit `/health` endpoint for backend

---

**Last Updated**: 2025  
**Deployment Target**: Render.com  
**Services**: FastAPI Backend + Vue.js Frontend
