# Learnify - Vue.js + FastAPI Stack

This is the Vue.js + FastAPI version of the Learnify application, converted from the original Streamlit implementation. The application provides AI-powered course generation with interactive quizzes.

## Architecture Overview

### Frontend (Vue.js)
- **Framework:** Vue 3 with Composition API
- **State Management:** Pinia
- **Routing:** Vue Router
- **HTTP Client:** Axios
- **Build Tool:** Vite
- **Styling:** Custom CSS (replicating Streamlit design)

### Backend (FastAPI)
- **Framework:** FastAPI
- **Database:** MongoDB (via pymongo)
- **AI Service:** Google Gemini AI
- **Authentication:** bcrypt for password hashing
- **File Processing:** PyPDF2, pdfplumber, python-docx, etc.

## Features

All features from the original Streamlit version are preserved:

- ✅ Document upload (PDF and other formats)
- ✅ URL-based document input
- ✅ AI-powered course generation
- ✅ Interactive quizzes with multiple question types:
  - Multiple choice
  - True/False
  - Fill in the blank
  - Short answer (with AI validation)
  - Matching
- ✅ User authentication (register/login)
- ✅ Progress tracking
- ✅ Course management
- ✅ Analytics

## Project Structure

```
learnify/
├── api/                      # FastAPI backend
│   ├── main.py              # Main FastAPI application
│   └── requirements.txt     # Backend dependencies
├── vue-frontend/            # Vue.js frontend
│   ├── src/
│   │   ├── components/      # Reusable Vue components
│   │   ├── views/          # Page components
│   │   ├── stores/         # Pinia stores
│   │   ├── services/       # API services
│   │   ├── router/         # Vue Router configuration
│   │   └── assets/         # Static assets and styles
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── backend/                 # Shared backend logic
│   ├── local_backend.py    # AI course generation
│   ├── mongo_auth.py       # Authentication
│   ├── mongo_course_manager.py  # Course management
│   └── ...                 # Other backend utilities
└── frontend/               # Original Streamlit frontend (preserved)
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- MongoDB instance (local or cloud)
- Google Gemini API key

### 1. Backend Setup

#### Install Python Dependencies

```bash
cd api
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `api/` directory:

```env
# Google AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/

# Optional: Debug mode
DEBUG_MODE=False
```

Alternatively, you can create a `.streamlit/secrets.toml` file in the project root (for compatibility):

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
MONGODB_URI = "mongodb://localhost:27017/"
COOKIE_ENCRYPTION_KEY = "your_strong_encryption_key_here"
```

#### Run the Backend

```bash
cd api
python main.py
```

The API will start on `http://localhost:8000`

You can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend Setup

#### Install Node Dependencies

```bash
cd vue-frontend
npm install
```

#### Run the Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## Running the Full Application

1. **Start MongoDB** (if running locally):
   ```bash
   mongod
   ```

2. **Start the FastAPI Backend**:
   ```bash
   cd api
   python main.py
   ```

3. **Start the Vue.js Frontend** (in a new terminal):
   ```bash
   cd vue-frontend
   npm run dev
   ```

4. **Access the Application**:
   Open your browser to `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### Course Generation
- `POST /api/course/generate/upload` - Generate course from uploaded file
- `POST /api/course/generate/url` - Generate course from URL

### Course Management
- `POST /api/course/save` - Save a course
- `GET /api/course/{course_id}` - Get course by ID
- `GET /api/courses` - List all courses for user
- `POST /api/course/{course_id}/progress` - Update progress
- `GET /api/course/{course_id}/progress` - Get progress

### Quiz
- `POST /api/quiz/validate-answer` - Validate short answer with AI

### Analytics
- `GET /api/analytics/courses` - Get course analytics

## Production Build

### Backend

For production, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
```

### Frontend

Build the frontend for production:

```bash
cd vue-frontend
npm run build
```

The built files will be in `vue-frontend/dist/`. Serve these with a web server like Nginx or Apache.

## Environment Variables

### Backend (.env)
- `GEMINI_API_KEY` - Google Gemini API key (required)
- `MONGODB_URI` - MongoDB connection string (required)
- `DEBUG_MODE` - Enable debug logging (optional, default: False)

### Frontend
The frontend uses the Vite proxy configuration to forward API requests to the backend during development. For production, configure your web server to proxy `/api` requests to the backend.

## Differences from Original Streamlit Version

### Architecture
- **Separated Concerns:** Frontend and backend are now completely separate applications
- **RESTful API:** All backend functionality is exposed through REST endpoints
- **Modern Frontend:** Vue.js provides a more responsive and modern UI experience
- **Better State Management:** Pinia provides predictable state management

### UI/UX
- **Same Visual Design:** The Vue.js frontend replicates the Streamlit gradient theme and card-based layout
- **Improved Responsiveness:** Better mobile experience with responsive design
- **Smoother Interactions:** Client-side state management reduces page reloads

### Preserved Features
- All course generation logic is unchanged
- Quiz question types work identically
- Authentication flow is the same
- Progress tracking maintains the same behavior
- MongoDB integration is unchanged

## Troubleshooting

### Backend Issues

1. **Import Errors:**
   - Make sure you're running from the correct directory
   - The `api/main.py` adds the `backend/` directory to the Python path

2. **MongoDB Connection:**
   - Ensure MongoDB is running
   - Check your `MONGODB_URI` in the `.env` file
   - Default: `mongodb://localhost:27017/`

3. **API Key Errors:**
   - Verify your `GEMINI_API_KEY` is correct
   - Check if the key has proper permissions

### Frontend Issues

1. **CORS Errors:**
   - The FastAPI backend is configured to allow requests from `localhost:3000`
   - If using different ports, update `api/main.py` CORS settings

2. **API Not Found:**
   - Ensure the backend is running on port 8000
   - Check the Vite proxy configuration in `vite.config.js`

3. **Build Errors:**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Frontend:** Vite automatically reloads on file changes
- **Backend:** Use `uvicorn api.main:app --reload` for auto-reload

### Debugging
- **Frontend:** Use Vue DevTools browser extension
- **Backend:** Set `DEBUG_MODE=True` in `.env` for verbose logging

### Adding New Features
1. **Backend:** Add new endpoints in `api/main.py`
2. **Frontend:** 
   - Add API calls in `src/services/api.js`
   - Update Pinia stores in `src/stores/`
   - Create/update components in `src/components/` or `src/views/`

## License

MIT License - See the original project for license details.

## Contributing

Contributions are welcome! Please ensure:
- All existing functionality is preserved
- New features have proper error handling
- Code follows the existing style
- Documentation is updated

## Support

For issues or questions:
- Check the API documentation at `http://localhost:8000/docs`
- Review this README and setup instructions
- Ensure all environment variables are properly configured
