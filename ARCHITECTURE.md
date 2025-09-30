# Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Browser)                          │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    Vue.js Frontend                         │   │
│  │                  (http://localhost:3000)                   │   │
│  │                                                            │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │  Components                                      │    │   │
│  │  │  - HomeView (file upload, course generation)    │    │   │
│  │  │  - CourseView (display sections & quizzes)      │    │   │
│  │  │  - QuizQuestion (all 5 quiz types)              │    │   │
│  │  │  - LoginView (auth forms)                       │    │   │
│  │  │  - CoursesView (list saved courses)             │    │   │
│  │  └──────────────────────────────────────────────────┘    │   │
│  │                                                            │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │  Pinia Stores (State Management)                │    │   │
│  │  │  - authStore: user, isAuthenticated             │    │   │
│  │  │  - courseStore: courses, currentCourse          │    │   │
│  │  └──────────────────────────────────────────────────┘    │   │
│  │                                                            │   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │  Services                                        │    │   │
│  │  │  - api.js (Axios HTTP client)                   │    │   │
│  │  │  - Router (Vue Router)                          │    │   │
│  │  └──────────────────────────────────────────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              │ HTTP/REST API                       │
│                              ▼                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                       SERVER (Backend)                              │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                   FastAPI Backend                          │   │
│  │                (http://localhost:8000)                     │   │
│  │                                                            │   │
│  │  API Endpoints:                                           │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Authentication                                   │   │   │
│  │  │  POST /api/auth/register                         │   │   │
│  │  │  POST /api/auth/login                            │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Course Generation                                │   │   │
│  │  │  POST /api/course/generate/upload                │   │   │
│  │  │  POST /api/course/generate/url                   │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Course Management                                │   │   │
│  │  │  POST /api/course/save                           │   │   │
│  │  │  GET  /api/course/{id}                           │   │   │
│  │  │  GET  /api/courses                               │   │   │
│  │  │  POST /api/course/{id}/progress                  │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Quiz Validation                                  │   │   │
│  │  │  POST /api/quiz/validate-answer                  │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                  Backend Modules                           │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │  local_backend.py                                   │  │   │
│  │  │  - generate_course()                                │  │   │
│  │  │  - validate_short_answer_with_ai()                  │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │  mongo_auth.py                                      │  │   │
│  │  │  - MongoAuthManager (user management)               │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │  mongo_course_manager.py                            │  │   │
│  │  │  - MongoCourseManager (course CRUD)                 │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │  file_security.py                                   │  │   │
│  │  │  - validate_file_security()                         │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External Services                              │
│                                                                     │
│  ┌────────────────────┐    ┌──────────────────────────────────┐   │
│  │    MongoDB         │    │       Google Gemini AI           │   │
│  │                    │    │                                  │   │
│  │  Collections:      │    │  - Course generation from docs   │   │
│  │  - users           │    │  - Short answer validation       │   │
│  │  - courses         │    │  - Content understanding         │   │
│  │  - progress        │    │                                  │   │
│  └────────────────────┘    └──────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### 1. Course Generation Flow

```
User uploads PDF
       │
       ▼
[Vue: HomeView]
  - Captures file
  - Shows progress bar
       │
       ▼
[Axios API call]
  POST /api/course/generate/upload
  Content-Type: multipart/form-data
       │
       ▼
[FastAPI Endpoint]
  - Validates file (size, type)
  - Reads file content
       │
       ▼
[local_backend.generate_course()]
  - Analyzes document
  - Sends to Gemini AI
  - Structures response
       │
       ▼
[Google Gemini AI]
  - Processes document
  - Generates course structure
  - Returns JSON
       │
       ▼
[FastAPI Response]
  { "success": true, "course_data": {...} }
       │
       ▼
[Vue: courseStore]
  - Stores in state
  - Updates UI
       │
       ▼
[Vue: HomeView]
  - Displays success
  - Shows course preview
```

### 2. Authentication Flow

```
User enters credentials
       │
       ▼
[Vue: LoginView]
  - Form validation
       │
       ▼
[Axios API call]
  POST /api/auth/login
  { username, password }
       │
       ▼
[FastAPI Endpoint]
  - Finds user in DB
  - Verifies password (bcrypt)
       │
       ▼
[MongoDB: users collection]
  - Query by username
  - Return user document
       │
       ▼
[FastAPI Response]
  { "success": true, "user": {...} }
       │
       ▼
[Vue: authStore]
  - Stores user in state
  - Saves to localStorage
       │
       ▼
[Vue: Router]
  - Redirects to home
  - Updates navigation
```

### 3. Quiz Answer Validation Flow

```
User answers question
       │
       ▼
[Vue: QuizQuestion]
  - Captures answer
  - Determines question type
       │
       ├─ Multiple Choice/True-False ─┐
       │                               ▼
       │                        [Client-side validation]
       │                        Compare with answer
       │                               │
       ├─ Short Answer ────────────────┤
       │                               ▼
       │                        [Axios API call]
       │                        POST /api/quiz/validate-answer
       │                               │
       │                               ▼
       │                        [FastAPI Endpoint]
       │                               │
       │                               ▼
       │                        [local_backend.validate_short_answer_with_ai()]
       │                               │
       │                               ▼
       │                        [Google Gemini AI]
       │                        - Compares answers semantically
       │                        - Returns is_correct + explanation
       │                               │
       │                               ▼
       │                        [FastAPI Response]
       │                        { "is_correct": true, "explanation": "..." }
       │                               │
       └───────────────────────────────┘
                                       │
                                       ▼
                            [Vue: QuizQuestion]
                            - Shows feedback
                            - Updates score
                                       │
                                       ▼
                            [Vue: CourseView]
                            - Emits score update
                            - Tracks progress
                                       │
                                       ▼
                            [Axios API call]
                            POST /api/course/{id}/progress
                                       │
                                       ▼
                            [MongoDB: progress collection]
                            - Updates user progress
```

## Technology Stack

### Frontend Layer
- **Vue 3**: Progressive framework
- **Vite**: Build tool & dev server
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client

### Backend Layer
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Python 3.9+**: Programming language

### Data Layer
- **MongoDB**: NoSQL database
- **pymongo**: Python driver

### External Services
- **Google Gemini AI**: Content generation & validation

## Deployment Architecture

```
                                  [Internet]
                                      │
                                      ▼
                            ┌──────────────────┐
                            │   Load Balancer  │
                            │   / Reverse Proxy│
                            │     (Nginx)      │
                            └──────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
           ┌─────────────────┐              ┌─────────────────┐
           │  Static Assets  │              │  API Servers    │
           │   (Frontend)    │              │   (Backend)     │
           │                 │              │                 │
           │  - CDN/S3       │              │  - Gunicorn     │
           │  - Netlify      │              │  - Docker       │
           │  - Vercel       │              │  - AWS EB       │
           └─────────────────┘              └─────────────────┘
                                                     │
                                    ┌────────────────┴────────────────┐
                                    │                                 │
                                    ▼                                 ▼
                          ┌──────────────────┐            ┌──────────────────┐
                          │    MongoDB       │            │  Google Gemini   │
                          │  (Atlas/Self)    │            │      API         │
                          └──────────────────┘            └──────────────────┘
```

## File Organization

```
learnify/
├── api/                    # New FastAPI backend
│   ├── main.py            # API endpoints
│   └── requirements.txt   # Dependencies
│
├── vue-frontend/          # New Vue.js frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Dependencies
│
├── backend/              # Existing backend modules (reused)
│   ├── local_backend.py
│   ├── mongo_auth.py
│   └── mongo_course_manager.py
│
└── frontend/             # Original Streamlit (preserved)
```

## Key Design Decisions

1. **Reuse Existing Backend Logic**: All core logic from `backend/` is reused by FastAPI
2. **RESTful API**: Clean separation between frontend and backend
3. **Stateless Backend**: Authentication via request parameters, easily scalable
4. **Component-Based UI**: Modular Vue components for maintainability
5. **Progressive Enhancement**: Basic functionality works, advanced features layered on
6. **Production Ready**: Both dev and production configurations included

## Performance Characteristics

- **Initial Load**: ~500ms (frontend assets)
- **API Response**: 50-200ms (database queries)
- **Course Generation**: 30-120s (AI processing, depends on document size)
- **Quiz Validation**: 1-3s (AI validation for short answers)
- **File Upload**: Depends on file size, max 20MB supported
