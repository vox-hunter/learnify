# Quickstart: AI Loom React Frontend

## Overview
This quickstart validates that the AI Loom React frontend correctly integrates with the existing Python backend to provide the complete user workflow from document upload through course completion.

## Prerequisites
- Python backend running on localhost:8501
- React frontend development server running
- Valid GEMINI_API_KEY configured in backend
- Sample PDF file for testing (educational content recommended)

## Test Scenarios

### Scenario 1: Guest User Course Generation
**Objective**: Verify guest users can upload PDFs and generate courses within usage limits.

**Steps**:
1. Open React frontend at http://localhost:3000
2. Verify home page displays without authentication required
3. Click "Upload File" method
4. Select a sample PDF file (< 10MB recommended)
5. Click "Generate Course" button
6. Monitor progress indicators showing real-time status
7. Wait for course generation completion (30-60 seconds expected)
8. Verify navigation to course page with interactive content

**Expected Results**:
- File upload succeeds with size validation
- Progress bar shows incremental updates with status messages
- Course page displays with title, sections, and quiz questions
- Question types include multiple choice, fill-in-blanks, true/false
- Progress tracking shows 0% initially

**Validation**:
```bash
# Check network requests
curl -X POST http://localhost:8501/api/documents/upload \
  -F "file=@sample.pdf" \
  -H "Content-Type: multipart/form-data"

# Expect 201 response with document ID
```

### Scenario 2: URL-Based Course Generation  
**Objective**: Verify course generation from publicly accessible PDF URLs.

**Steps**:
1. Navigate to home page
2. Select "Provide URL" method
3. Enter valid PDF URL: `https://example.com/sample-educational.pdf`
4. Click "Generate Course" button
5. Monitor backend processing of URL fetch and validation
6. Verify course generation completes successfully

**Expected Results**:
- URL validation prevents invalid/non-PDF URLs
- Backend fetches and processes remote PDF
- Generated course structure matches uploaded file workflow
- No file size display for URL method (backend handles limits)

### Scenario 3: Guest Usage Limit Enforcement
**Objective**: Verify guest users are limited to 3 course generations.

**Steps**:
1. Clear browser local storage/cookies
2. Generate 3 courses as guest user following Scenario 1
3. Verify usage counter increments: "2 guest courses remaining" → "1 guest course remaining" → "0 guest courses remaining"
4. Attempt to generate 4th course
5. Verify system prevents generation and prompts for login

**Expected Results**:
- Usage counter displays accurately after each generation
- 4th generation attempt shows error: "Guest courses limit reached"
- Login page becomes accessible with clear messaging
- Previous generated courses remain accessible

### Scenario 4: User Authentication Flow
**Objective**: Verify login/logout functionality integrates with backend.

**Steps**:
1. Click "Login" or navigate to login page
2. Enter valid credentials (configured in backend)
3. Verify successful authentication redirects to home page
4. Check user session persistence across page refreshes
5. Generate course as authenticated user
6. Verify no usage limits apply
7. Logout and confirm session termination

**Expected Results**:
- Login form validates email format and password requirements
- Successful login shows user name/email in UI
- Authenticated users see "unlimited access" messaging
- Session token stored securely (httpOnly cookie preferred)
- Logout clears session and returns to guest state

### Scenario 5: Quiz Interaction and Progress Tracking
**Objective**: Verify interactive quiz functionality and progress persistence.

**Steps**:
1. Generate any course following Scenario 1
2. Navigate through course sections using Previous/Next buttons
3. Answer quiz questions in each section:
   - Select multiple choice answers
   - Fill in blank fields for fill-in-the-blanks questions
   - Submit true/false responses
   - Complete matching questions if present
4. Verify immediate feedback after each answer
5. Check progress meter updates with correct score calculation
6. Complete entire course and verify final score display

**Expected Results**:
- Each question type renders correctly with appropriate UI
- Real-time feedback shows correct/incorrect with explanations
- Progress bar updates incrementally: "Section 1 of 5 (20%)"
- Score tracking: "Current Score: 8/10 (80%)"
- Fill-in-the-blanks component maintains existing functionality
- Section navigation preserves answered questions

### Scenario 6: Error Handling and Edge Cases
**Objective**: Verify robust error handling for common failure scenarios.

**Steps**:
1. **Large File Test**: Upload PDF > 20MB, verify rejection
2. **Invalid File Test**: Upload non-PDF file (.txt, .docx), verify validation
3. **Corrupted File Test**: Upload corrupted PDF, verify backend error handling
4. **Network Failure Test**: Disconnect internet during generation, verify timeout handling
5. **Invalid URL Test**: Provide non-existent URL, verify error messaging
6. **Backend Unavailable Test**: Stop backend service, verify connection error display

**Expected Results**:
- File size errors show clear message: "File size exceeds 20MB limit"
- File type errors specify allowed formats: "Only PDF files are supported"
- Network errors provide retry options and clear messaging
- All errors display user-friendly messages, not technical stack traces
- Loading states clear properly after errors
- Users can recover and retry without page refresh

### Scenario 7: Mobile Responsiveness
**Objective**: Verify UI adapts properly to mobile screen sizes.

**Steps**:
1. Open React frontend on mobile device or browser dev tools mobile view
2. Verify responsive breakpoints at 768px, 1024px per constitution
3. Test file upload functionality on mobile
4. Navigate through course sections with touch interaction
5. Complete quiz questions with mobile-optimized input controls
6. Verify progress indicators display clearly on small screens

**Expected Results**:
- Layout adapts at constitutional breakpoints (768px, 1024px, 1440px)
- File upload button accessible with mobile touch
- Quiz questions render clearly without horizontal scrolling
- Navigation buttons sized appropriately for touch interaction
- Progress bars and status messages remain visible

## Performance Validation

### Bundle Size Check
```bash
# After build, verify bundle size meets constitutional limits
npm run build
du -sh build/static/js/*.js | sort -h
# Main bundle should be < 500KB gzipped
```

### Loading Performance
```bash
# Lighthouse CI or manual audit
lighthouse http://localhost:3000 --output json
# Expect Performance score ≥ 90
# Expect Accessibility score ≥ 90
# Expect Best Practices score ≥ 90
```

### API Response Times
```bash
# Monitor course generation performance
time curl -X POST http://localhost:8501/api/courses/generate \
  -H "Content-Type: application/json" \
  -d '{"documentId": "doc_123456"}'
# Should initiate within 2 seconds
# Total generation: 30-60 seconds for typical PDFs
```

## Success Criteria
All test scenarios must pass with:
- ✅ No JavaScript console errors
- ✅ Proper error handling with user-friendly messages  
- ✅ Responsive design at all breakpoints
- ✅ Performance scores ≥ 90 in Lighthouse
- ✅ Bundle size < 500KB gzipped
- ✅ Course generation completes within 60 seconds for typical PDFs
- ✅ All existing backend functionality preserved
- ✅ Custom components (fill-in-blanks) work identically to Streamlit version

## Troubleshooting
- **Backend Connection**: Verify Python backend running on expected port
- **CORS Issues**: Check backend CORS configuration allows frontend origin
- **File Upload Failures**: Confirm backend file size limits and validation
- **Authentication Issues**: Verify backend session/token management configuration
- **Performance Issues**: Run bundle analysis to identify heavy dependencies