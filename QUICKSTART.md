# Quick Start Guide - Vue.js + FastAPI Learnify

This guide will help you get the Vue.js + FastAPI version of Learnify up and running quickly.

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed  
- [ ] MongoDB running (local or cloud)
- [ ] Google Gemini API key

## 5-Minute Setup

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### Step 2: Configure Environment

Create `api/.env`:
```bash
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017/
```

### Step 3: Start MongoDB

**Mac (with Homebrew):**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

**Windows:**
- Start MongoDB from Services or
- Run `mongod` in a terminal

**Using Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Step 4: Install & Run Backend

```bash
# Navigate to API directory
cd api

# Install dependencies (one-time)
pip install -r requirements.txt

# Start the backend server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open!

### Step 5: Install & Run Frontend

Open a **new terminal**:

```bash
# Navigate to frontend directory
cd vue-frontend

# Install dependencies (one-time)
npm install

# Start the development server
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:3000/
```

### Step 6: Open the App

Open your browser to: **http://localhost:3000**

## Quick Test

1. **Register an account:**
   - Click "Login" in the navigation
   - Switch to "Register" tab
   - Fill in the form and submit

2. **Generate a course:**
   - Go back to home page
   - Upload a PDF file or provide a PDF URL
   - Click "Generate Course"
   - Wait for the AI to process (may take 1-2 minutes)

3. **Take the quiz:**
   - Answer the quiz questions
   - See your score update in real-time

## Troubleshooting Quick Fixes

### Backend won't start

**Problem:** ImportError or module not found
```bash
# Solution: Install from project root
cd /path/to/learnify
pip install -r api/requirements.txt
```

**Problem:** MongoDB connection error
```bash
# Solution: Check if MongoDB is running
# Mac/Linux:
ps aux | grep mongod

# If not running, start it:
mongod --dbpath /path/to/data
```

### Frontend won't start

**Problem:** Module not found
```bash
# Solution: Clean install
cd vue-frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Port 3000 already in use
```bash
# Solution: Use a different port
PORT=3001 npm run dev
# Then update CORS in api/main.py to include :3001
```

### API requests failing

**Problem:** CORS errors in browser console

**Solution:** Check that:
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. `api/main.py` includes your frontend port in CORS origins:
   ```python
   allow_origins=["http://localhost:3000", ...]
   ```

### Course generation fails

**Problem:** "Invalid API key" error

**Solution:** 
1. Verify your API key is correct in `api/.env`
2. Check that the file starts with `GEMINI_API_KEY=`
3. No spaces around the `=` sign
4. Restart the backend after changing `.env`

## Development Workflow

### Making Changes

**Backend changes:**
```bash
# Stop the server (Ctrl+C)
# Make your changes to api/main.py or backend/*.py
# Restart the server
python api/main.py
```

**Frontend changes:**
- Changes auto-reload with Vite
- Just save your files in `vue-frontend/src/`
- Browser updates automatically

### Viewing Logs

**Backend logs:**
- Visible in the terminal where you ran `python main.py`
- Set `DEBUG_MODE=True` in `.env` for verbose logging

**Frontend logs:**
- Open browser DevTools (F12)
- Check Console tab for logs
- Check Network tab for API requests

### Testing API Endpoints

Visit: **http://localhost:8000/docs**

This opens Swagger UI where you can:
- See all available endpoints
- Test endpoints directly
- View request/response schemas

## Common Tasks

### Add a new API endpoint

1. Edit `api/main.py`
2. Add your endpoint function:
   ```python
   @app.post("/api/your-endpoint")
   async def your_function():
       return {"message": "success"}
   ```
3. Save - the server will auto-reload (if using `--reload` flag)

### Add a new Vue component

1. Create file in `vue-frontend/src/components/YourComponent.vue`
2. Import in a view: `import YourComponent from '@/components/YourComponent.vue'`
3. Use in template: `<YourComponent />`

### Update styling

Edit `vue-frontend/src/assets/main.css` for global styles or use `<style scoped>` in individual components.

## Next Steps

- Read the full [VUE_FASTAPI_README.md](./VUE_FASTAPI_README.md)
- Explore the API documentation at http://localhost:8000/docs
- Check out the Vue.js [official documentation](https://vuejs.org/)
- Learn about FastAPI at https://fastapi.tiangolo.com/

## Getting Help

If you encounter issues:

1. Check the terminal output for error messages
2. Look at browser DevTools console
3. Verify all prerequisites are installed
4. Ensure MongoDB is running
5. Confirm API key is valid

## Stopping the Application

1. **Stop Frontend:** Press `Ctrl+C` in the frontend terminal
2. **Stop Backend:** Press `Ctrl+C` in the backend terminal
3. **Stop MongoDB** (optional):
   ```bash
   # Mac
   brew services stop mongodb-community
   
   # Linux
   sudo systemctl stop mongod
   
   # Docker
   docker stop mongodb
   ```

## Production Deployment

For deploying to production, see the "Production Build" section in [VUE_FASTAPI_README.md](./VUE_FASTAPI_README.md).

---

**Congratulations!** You now have a fully functional Vue.js + FastAPI version of Learnify running locally. 🎉
