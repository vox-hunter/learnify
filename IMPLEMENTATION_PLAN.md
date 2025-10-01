# Implementation Plan - Bug Fixes & New Features
**Date**: October 1, 2025

## Issues to Fix


### 3.  Email Verification Implementation
**Problem**: New users can register but email verification is not implemented in frontend.

**Backend Already Has**:
- `send_verification_email()` - sends 6-digit code
- `verify_code()` - validates code
- `store_verification_code()` - stores code in DB

**Solution**:
- Create multi-step registration flow:
  1. Collect user details
  2. Send verification email
  3. Verify code
  4. Complete registration
- Add verification endpoints to API
- Update RegisterView.vue with verification step

**Files to Create/Modify**:
- `api/main.py` - Add `/api/auth/verify` endpoint
- `vue-frontend/src/views/RegisterView.vue` - Add verification step

---

### 6.  Account Dashboard
**Problem**: No account settings page for users.

**Backend Already Has**:
- `update_user_details()` - Update name, email, etc.
- `update_user_password()` - Change password
- `delete_user_account()` - Delete account

**Solution**:
- Create AccountView.vue with tabs:
  - Profile: Edit name, email
  - Security: Change password
  - Danger Zone: Delete account
- Add API endpoints for account management
- Add route and navigation link

**Files to Create/Modify**:
- `api/main.py` - Add account management endpoints
- `vue-frontend/src/views/AccountView.vue` - Create new view
- `vue-frontend/src/router/index.js` - Add route
- `vue-frontend/src/App.vue` - Add navigation link

---

### 7.  Admin Controls
**Problem**: No admin debugging tools.

**Solution**:
- Check if user email is "vidyutsanthosh4@gmail.com" on login
- Set `isAdmin: true` in user object
- In CourseView.vue, show admin panel with:
  - "Complete All" button - marks all questions correct
  - "Reset Progress" button - clears all progress
- Admin controls only visible to admin user

**Files to Modify**:
- `api/main.py` - Add `is_admin` flag to login response
- `vue-frontend/src/stores/auth.js` - Store isAdmin
- `vue-frontend/src/views/CourseView.vue` - Add admin controls
- `backend/mongo_course_manager.py` - Add admin methods if needed

---

### 8. Google OAuth
**Problem**: Google OAuth not implemented in Vue frontend.

**Backend Already Has**:
- `google_oauth_simple.py` - OAuth flow
- `get_google_oauth_url()` - Generate OAuth URL
- `create_user_from_google()` - Create user from Google data

**Solution**:
- Add "Sign in with Google" button to LoginView
- Create OAuth callback handler
- Add API endpoints for OAuth flow
- Handle OAuth redirect and token exchange

**Files to Create/Modify**:
- `api/main.py` - Add OAuth endpoints
- `vue-frontend/src/views/LoginView.vue` - Add Google button
- `vue-frontend/src/views/OAuthCallback.vue` - Create callback handler
- `vue-frontend/src/router/index.js` - Add OAuth callback route

---

### Implement course conclusion. after the user finishes all questions display a conclusion overview on how many questions were correct and a summary of the course.

### Implement a progress bar that shows how many questions the user has completed out of the total number of questions in the course. it should conatin 2 colours one for completed questions and one for remaining questions.whioch should be visible while the user is doing the course

### Implement a realtime status/progress indicator that shows the user when the course is being generated and when it is ready to be started. add status messages for each process that is happening in the backend like "generating course content", "creating quiz questions", "saving to database" etc.


2. **Backend API Updates** (Issues 3, 4, 6, 7)
3. **Frontend Components** (Issues 3, 4, 6, 7, 8)
4. **Testing & Integration**

---

## Estimated Files to Modify

### Backend
- `api/main.py` - Add 10+ new endpoints
- `backend/mongo_auth.py` - Update login logic
- `backend/mongo_course_manager.py` - Add admin methods

### Frontend
- `vue-frontend/src/components/QuizQuestion.vue` - Fix dialog bug
- `vue-frontend/src/views/HomeView.vue` - Fix guest redirect
- `vue-frontend/src/views/LoginView.vue` - Add email login + Google OAuth
- `vue-frontend/src/views/RegisterView.vue` - Add email verification
- `vue-frontend/src/views/CourseView.vue` - Add admin controls
- `vue-frontend/src/views/AccountView.vue` - CREATE NEW
- `vue-frontend/src/views/OAuthCallback.vue` - CREATE NEW
- `vue-frontend/src/stores/auth.js` - Fix remember me + admin flag
- `vue-frontend/src/router/index.js` - Add routes
- `vue-frontend/src/App.vue` - Add navigation

**Total**: ~13 files to modify, 2 new files to create
