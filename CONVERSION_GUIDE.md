# Streamlit to Vue.js + FastAPI Conversion Guide

This document details how the original Streamlit application was converted to Vue.js + FastAPI architecture while preserving all functionality.

## Conversion Mapping

### Frontend Conversion

#### Original Streamlit Pages → Vue.js Views

| Streamlit File | Vue.js View | Purpose |
|----------------|-------------|---------|
| `frontend/main.py` | `src/App.vue` + `src/router/index.js` | Main app and routing |
| `frontend/frontend.py` | `src/views/HomeView.vue` | Course generation interface |
| `pages/2_🔐_Login.py` | `src/views/LoginView.vue` | Authentication |
| `pages/3_Course.py` | `src/views/CourseView.vue` | Course display and quizzes |
| `pages/4_Privacy.py` | `src/views/PrivacyView.vue` | Privacy policy |
| `pages/5_Terms.py` | `src/views/TermsView.vue` | Terms & conditions |
| N/A (sidebar) | `src/views/CoursesView.vue` | Course list |

#### Streamlit Components → Vue.js Components

| Streamlit Component | Vue.js Component | Implementation |
|---------------------|------------------|----------------|
| `st.file_uploader` | `<input type="file">` | Custom styled file input |
| `st.text_input` | `<input class="form-input">` | Custom form inputs |
| `st.button` | `<button class="btn">` | Styled buttons |
| `st.progress` | `<div class="progress-bar">` | Custom progress bar |
| `st.error` / `st.success` | `<div class="alert">` | Alert components |
| `st_fill_in_the_blanks` | `QuizQuestion.vue` | Integrated quiz component |
| `st.radio` | Vue tabs | Tab-based selection |
| `st.selectbox` | `<select class="form-select">` | Custom dropdown |

### Backend Conversion

#### Streamlit Backend → FastAPI Endpoints

| Original Function | FastAPI Endpoint | Method | Purpose |
|-------------------|------------------|--------|---------|
| `generate_course()` | `/api/course/generate/upload` | POST | Generate course from file |
| `generate_course()` | `/api/course/generate/url` | POST | Generate course from URL |
| `validate_short_answer_with_ai()` | `/api/quiz/validate-answer` | POST | AI answer validation |
| `MongoAuthManager.add_user()` | `/api/auth/register` | POST | User registration |
| `MongoAuthManager.find_user()` | `/api/auth/login` | POST | User login |
| `MongoCourseManager.save_course()` | `/api/course/save` | POST | Save course |
| `MongoCourseManager.get_course()` | `/api/course/{id}` | GET | Get course |
| `MongoCourseManager.get_user_courses()` | `/api/courses` | GET | List courses |
| `MongoCourseManager.update_progress()` | `/api/course/{id}/progress` | POST | Update progress |

### State Management Conversion

#### Streamlit Session State → Pinia Stores

| Streamlit Session State | Pinia Store | State Variables |
|------------------------|-------------|-----------------|
| `st.session_state.username` | `authStore` | `user`, `isAuthenticated` |
| `st.session_state.authentication_status` | `authStore` | `isAuthenticated` |
| `st.session_state.course_data` | `courseStore` | `currentCourse` |
| `st.session_state.current_section` | `CourseView` local state | `currentSectionIndex` |
| `st.session_state.current_score` | `CourseView` local state | `score` |

## Feature Preservation

### ✅ Preserved Features

1. **Document Upload**
   - File size validation (20MB)
   - PDF support
   - Document conversion (DOCX, PPTX, etc.)
   - URL-based input

2. **Course Generation**
   - AI-powered via Google Gemini
   - Multi-format support
   - Progress tracking during generation
   - Error handling

3. **Quiz Types**
   - Multiple Choice: Full preservation with A/B/C/D options
   - True/False: Identical behavior
   - Fill in the Blank: Input-based with validation
   - Short Answer: AI validation preserved
   - Matching: Drag-and-drop style selection

4. **Authentication**
   - Registration with email validation
   - Login system
   - Password hashing (bcrypt)
   - Session management
   - OAuth placeholder for future

5. **Course Management**
   - Save courses to database
   - Load saved courses
   - Progress tracking per question
   - Score calculation
   - Section navigation

6. **UI/UX**
   - Same gradient color scheme (#06b6d4 cyan)
   - Card-based layout
   - Responsive design
   - Loading states
   - Error messages
   - Success feedback

### 🆕 Improvements

1. **Performance**
   - Client-side rendering (faster UI updates)
   - Optimistic updates
   - Better state management
   - Reduced server round-trips

2. **Architecture**
   - Clean separation of concerns
   - RESTful API design
   - Scalable frontend/backend
   - Better for microservices

3. **Developer Experience**
   - Hot module replacement
   - Better debugging tools
   - TypeScript support ready
   - Component reusability

4. **Deployment**
   - Frontend can be served from CDN
   - Backend can scale independently
   - Better for containerization
   - Multiple deployment options

## Code Comparison Examples

### Example 1: File Upload

**Streamlit:**
```python
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    course_data, error = generate_course(file_content=file_bytes, filename=uploaded_file.name)
```

**Vue.js + FastAPI:**
```vue
<!-- Vue Template -->
<input type="file" @change="handleFileChange" accept=".pdf" />
<button @click="generateCourse">Generate</button>

<!-- Vue Script -->
async function generateCourse() {
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  const response = await api.post('/course/generate/upload', formData)
}
```

```python
# FastAPI
@app.post("/api/course/generate/upload")
async def generate_course_from_upload(file: UploadFile = File(...)):
    file_bytes = await file.read()
    course_data, error = generate_course(file_content=file_bytes, filename=file.filename)
    return {"course_data": course_data}
```

### Example 2: Authentication

**Streamlit:**
```python
if st.session_state.get('authentication_status'):
    st.write(f"Welcome {st.session_state['name']}")
else:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            user = manager.find_user_by_username(username)
            if user and manager.verify_password(password, user["password"]):
                st.session_state['authentication_status'] = True
```

**Vue.js + FastAPI:**
```vue
<!-- Vue -->
<template>
  <div v-if="isAuthenticated">
    Welcome {{ user.name }}
  </div>
  <form v-else @submit.prevent="handleLogin">
    <input v-model="username" />
    <input v-model="password" type="password" />
    <button type="submit">Login</button>
  </form>
</template>

<script setup>
const authStore = useAuthStore()
async function handleLogin() {
  await authStore.login(username, password)
}
</script>
```

```python
# FastAPI
@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    user = auth_manager.find_user_by_username(credentials.username)
    if user and auth_manager.verify_password(credentials.password, user["password"]):
        return {"success": True, "user": user}
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Example 3: Quiz Display

**Streamlit:**
```python
for question in section['quiz']:
    st.markdown(f"**{question['question']}**")
    if question['type'] == 'multiple_choice':
        selected = st.radio("Choose:", question['options'], key=f"q_{idx}")
        if selected == question['answer']:
            st.success("Correct!")
```

**Vue.js:**
```vue
<div v-for="question in quiz" :key="question.id">
  <h4>{{ question.question }}</h4>
  <div v-if="question.type === 'multiple_choice'">
    <div 
      v-for="option in question.options"
      @click="selectAnswer(option)"
      :class="['option', { correct: isCorrect }]"
    >
      {{ option }}
    </div>
  </div>
</div>
```

## Migration Benefits

### For Users
- ✅ Faster, more responsive interface
- ✅ Better mobile experience
- ✅ Offline capability potential
- ✅ Modern UI/UX patterns

### For Developers
- ✅ Easier to maintain and scale
- ✅ Better testing capabilities
- ✅ More deployment options
- ✅ Industry-standard architecture

### For Operations
- ✅ Frontend and backend scale independently
- ✅ Static frontend can be cached/CDN'd
- ✅ Better monitoring and logging
- ✅ Easier to containerize

## Testing Equivalence

To verify the conversion maintains functionality:

1. **Upload a PDF** → Should generate identical course structure
2. **Answer quizzes** → Should validate answers the same way
3. **Create account** → Should hash passwords and store correctly
4. **Save progress** → Should track progress identically
5. **Navigate sections** → Should maintain same navigation flow

## Known Differences

### Intentional Changes
1. **No streaming UI updates during generation** - Could be added with WebSockets if needed
2. **Separate auth state** - Uses localStorage instead of cookies by default
3. **Static site deployment** - Frontend can be served from CDN

### Not Yet Implemented
1. **OAuth (Google login)** - Placeholder exists, needs full implementation
2. **Email verification** - Backend exists, frontend needs integration
3. **Advanced analytics** - Basic analytics implemented, can be expanded

## Conclusion

The conversion successfully replicates all core functionality of the Streamlit application while providing:
- Better performance
- Modern architecture
- Improved scalability
- Enhanced developer experience
- More deployment options

All essential features work identically, and the visual design closely matches the original Streamlit version.
