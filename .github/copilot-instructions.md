# Learnify (AI Loom) - AI Coding Agent Instructions

## Project Overview
Learnify is an AI-powered course and quiz generator that converts PDF documents and other files into interactive learning experiences with multiple question types. The system uses Google's Gemini AI for content generation and supports both authenticated users and guest accounts with limitations.

**Tech Stack:**
- **Frontend:** Vue 3 + Vite + Pinia (state management) + Vue Router
- **Backend:** FastAPI (Python) with MongoDB for persistence
- **AI:** Google Gemini 2.0 Flash for course generation and answer validation
- **Deployment:** Render (separate frontend static site + backend web service)
- **CRITICAL** Streamlit is NOT used in this project and it is DEPRECATED.

## Architecture

### Service Boundaries
```
Vue Frontend (port 3000) ←→ FastAPI Backend (port 8000) ←→ MongoDB + Gemini AI
```

**Frontend (`vue-frontend/`):** Single-page app with router-based navigation. State managed via Pinia stores (`auth.js`, `course.js`). API calls handled by `services/api.js` with auto-attached auth params.

**Backend (`api/main.py`):** FastAPI app serving REST endpoints. Imports business logic from `backend/` modules:
- `local_backend.py` - Core AI integration and course generation
- `mongo_auth.py` - User authentication (bcrypt hashing, email verification)
- `mongo_course_manager.py` - Course CRUD operations
- `file_security.py` - File validation against security threats and Gemini format support

**Data Flow for Course Generation:**
1. User uploads file in `HomeView.vue` → `useCourseStore().generateCourse()`
2. Store sends file to `/chat/message` endpoint with message "Please generate a course from this file."
3. `ChatSessionManager.send_message()` processes the file and sends to Gemini AI with system instruction
4. AI analyzes file content and decides whether to generate a course based on content suitability
5. If suitable, Gemini returns JSON course structure; `chat_manager.py` detects and parses it
6. Frontend receives course data via `is_course` flag and `course_data` in response, stores in `courseStore`, navigates to `CourseView.vue`

### Critical State Management Pattern
**Auth Store (`stores/auth.js`):**
- Dual storage: localStorage (persistent) + sessionStorage (session-only) based on "remember me"
- Admin detection: `isAdmin` flag set server-side for `vidyutsanthosh4@gmail.com`
- Cookie helpers for "remember me" functionality
- Auth params auto-attached via axios interceptor (username in query params)

**Course Store (`stores/course.js`):**
- Guest users: Limited to 2 course generations, tracked via `guestCourseCount` in localStorage
- Authenticated users: Unlimited courses saved to MongoDB via `mongo_course_manager.py`
- Hybrid storage: Courses saved to both localStorage (for offline) and MongoDB (for cloud sync)

## Key Conventions & Patterns

### 1. Pydantic Schema Validation
Course generation uses strict Pydantic models in `local_backend.py`:
```python
class QuizItem(BaseModel):
    type: Literal["multiple_choice", "fill_in_the_blank", "match", "short_answer", "true_false"]
    question: str
    options: Optional[List[str]]
    answer: Union[str, bool, List[str], ArbitraryMapping]

class Section(BaseModel):
    section_title: str
    explanation: str
    quiz: List[QuizItem]
    subsections: Optional[List['Section']]  # Recursive nesting
```
Always maintain schema compatibility when modifying course structure.

### 2. Question Type Handling in `QuizQuestion.vue`
Component uses computed properties to determine question type:
- `isMultipleChoice` - Options array with single string answer
- `isTrueFalse` - Boolean answer
- `isFillInBlank` - Short string answer (case-insensitive matching)
- `isShortAnswer` - Long-form text validated via AI (calls `/quiz/validate-answer`)
- `isMatching` - Answer is object/ArbitraryMapping with key-value pairs

When adding question types, update both backend schema and frontend rendering logic.

**File Security & Conversion Pipeline**
`file_security.py` enforces:
- Max file size: 10MB (`MAX_FILE_SIZE`)
- Max content: 15,000 words (`MAX_CONTENT_WORDS`)
- Blocked extensions: `.exe`, `.bat`, `.py`, archives, etc. (see `DANGEROUS_EXTENSIONS`)
- Allowed: Documents, images, audio, video (see `SAFE_EXTENSIONS`)

Conversion flow (in `chat_manager.py`):
1. File validation happens at `/chat/message` endpoint before processing
2. File is sent directly to Gemini AI as bytes with MIME type
3. AI processes file content and determines if course generation is appropriate
4. System instruction guides AI to detect educational content and output JSON when suitable

### 4. Admin Controls Pattern
Admin user (hardcoded email check in `api/main.py:login`) gets special features in `CourseView.vue`:
- "Complete All" button - marks all questions correct
- "Reset Progress" button - clears progress
- Only visible when `authStore.user.isAdmin === true`

Extend this pattern for other admin features by checking `isAdmin` flag.

### 5. Status Callbacks for Real-Time Updates
Chat messages support streaming responses for real-time updates. Course generation happens through the chat interface, providing natural feedback to the user about the processing status.

## Development Workflows

### Local Development Setup
**Start command (Windows):** `start-dev.bat`
1. Checks for `api/.env` with `GEMINI_API_KEY` and `MONGODB_URI`
2. Starts FastAPI: `cd api && uvicorn main:app --reload --host localhost --port 8000`
3. Starts Vite: `cd vue-frontend && npm run dev` (port 3000)
4. Or just run './start-dev.bat'

**Environment Variables Required:**
```
GEMINI_API_KEY=<your-key>
MONGODB_URI=mongodb+srv://...
```

### Testing Quiz Answer Validation
Short answer validation uses AI (`validate_short_answer_with_ai()` in `local_backend.py`):
- Calls Gemini with validation prompt
- Returns `(is_correct: bool, explanation: str)`
- Temperature 0.3 for consistency
- JSON response format enforced

Test by submitting short answer questions in UI - watch network tab for `/quiz/validate-answer` POST.

### Deployment to Render
**Configured in `render.yaml`:**
- Backend: Web service, runs `uvicorn main:app` on port `$PORT`
- Frontend: Static site, builds with `npm run build`, serves from `dist/`
- Environment: `VITE_API_URL` must point to backend URL (e.g., `https://ai-loom-backend.onrender.com`)

**CORS Configuration:** Backend `main.py` allows origins from `localhost:3000` and production domain. Add new domains to `allow_origins` list.

## Common Pitfalls

1. **Forgetting to serialize Pydantic models:** When saving courses, call `.model_dump()` on Pydantic objects before MongoDB insertion (see `mongo_course_manager.py:save_course()`).

2. **Guest course limit confusion:** Guest limit applies to *saving* courses, not generating. Check `canGenerateCourse` computed property in `course.js` before showing save UI.

3. **File conversion errors:** If upload fails, check:
   - File extension against `SAFE_EXTENSIONS` in `file_security.py`
   - Conversion dependencies installed (`pip install python-docx pypdf2 pdfplumber`)
   - Max file size not exceeded

4. **Auth state sync:** `localStorage.getItem('username')` is auto-attached to all API requests via axios interceptor. Don't manually add username to request params.

5. **Question type mismatches:** Ensure `question.type` matches exact literals in Pydantic schema. Gemini sometimes returns "true or false" instead of "true_false" - both are accepted via schema aliases.

## Key Files Reference

**Entry Points:**
- `vue-frontend/src/main.js` - Vue app initialization
- `api/main.py` - FastAPI app and all REST endpoints

**Core Business Logic:**
- `backend/chat_manager.py` - AI chat sessions and course generation via chat
- `vue-frontend/src/views/CourseView.vue` - Main learning interface with quiz rendering
- `vue-frontend/src/components/QuizQuestion.vue` - Individual question rendering logic

**State & Services:**
- `vue-frontend/src/stores/auth.js` - Authentication state (login, register, remember me)
- `vue-frontend/src/stores/course.js` - Course state (generate, save, load, guest limits)
- `vue-frontend/src/services/api.js` - Axios instance with auth interceptor

**Database Modules:**
- `backend/mongo_auth.py` - User CRUD, password hashing, email verification
- `backend/mongo_course_manager.py` - Course CRUD, progress tracking

DO NOT EXPLAIN TOO MUCH TO THE USER AFTER YOU FINISH A TASK. JUST ANSWER THE USER PROMPT AS CONCISELY AS POSSIBLE. If you finished a task, say "Task complete." DO NOT CREATE ANY DOCUMENTATION OR MARKDOWN FILES. FINISH THE TASK AS SOON AS YOU CAN AND REPLY "TASK COMPLETE". DO NOT CREATE A SUMMARY OF WHAT YOU DID.
