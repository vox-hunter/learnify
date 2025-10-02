# AI Quiz and Course Generator

An application that uses AI to generate quizzes and courses from PDF documents.

## Features

- Upload a PDF file or provide a URL to a PDF document
- Generate a course with quizzes based on the PDF content
- Interactive quiz with multiple question types:
  - Multiple choice
  - Fill in the blank
  - Short answer
  - True/False
  - Matching
- Track your score as you answer questions
- Sections and subsections for organized learning

## How to Use

1. Choose between uploading a PDF file or providing a URL to a PDF document
2. Click "Generate Course"
3. Navigate through the sections using the "Previous Section" and "Next Section" buttons
4. Answer the quiz questions and get immediate feedback
5. Track your progress with the score meter

## Technical Details

This application uses the following technologies:

- Streamlit for the web interface
- Google's Gemini AI for content generation
- Custom Streamlit components for enhanced UI

## Getting Started

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up your API key:
   Create a `.env` file in the root directory with the following content:

   ```plaintext
   GEMINI_API_KEY=your_api_key_here
   ```
   
3. Run the application:

   ```bash
   streamlit run frontend/main.py
   ```

## File Structure

The repository is organized into separate frontend and backend directories:

### Frontend (`frontend/`)
- `main.py`: Entry point for the Streamlit application
- `frontend.py`: Main user interface implementation
- `pages/`: Streamlit pages for different app sections
- `utils/`: Frontend utilities (lazy imports, styling, navigation)
- `st_fill_in_the_blanks/`: Custom React component for fill-in-the-blank questions
- `.streamlit/`: Streamlit configuration files
- `*.html`: Static HTML pages and templates

### Backend (`backend/`)
- `local_backend.py`: Core AI processing and course generation
- `mongo_auth.py`: Authentication system
- `mongo_course_manager.py`: Course data management
- `file_security.py`, `file_converter.py`: File processing and security
- `google_oauth.py`: OAuth authentication
- `email_verification.py`: Email services
- `prompt.txt`, `sys_ins.txt`: AI prompt templates and system instructions
- `test_consolidated.py`: Backend tests

## Features in Detail

### Question Types Supported

1. **Multiple Choice**: Select from multiple options
2. **Fill in the Blank**: Custom interactive component with visual blanks
3. **Short Answer**: Text area for detailed responses  
4. **True/False**: Binary choice questions
5. **Matching**: Interactive drag-and-drop style matching interface

### Scoring System

- Real-time score tracking
- Progress indication across all sections
- Prevents double-scoring for the same question
- Visual feedback for correct/incorrect answers

### Course Navigation

- Section-based navigation with Previous/Next buttons
- Support for nested subsections
- Organized content presentation

## Deployment

### Production Deployment on Render

This application can be deployed to Render web service with both the Vue.js frontend and FastAPI backend.

**Quick Start:**
1. See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete deployment guide
2. See [DEPLOYMENT_COMMANDS.md](DEPLOYMENT_COMMANDS.md) for quick command reference

**Key Files:**
- `render.yaml` - Automated deployment configuration
- `api/requirements.txt` - Backend dependencies
- `vue-frontend/package.json` - Frontend dependencies

**Build Commands:**
- Backend: `pip install -r api/requirements.txt`
- Frontend: `cd vue-frontend && npm install && npm run build`

**Start Commands:**
- Backend: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Frontend: Static site from `vue-frontend/dist`

For detailed instructions, environment variables, and troubleshooting, see the full deployment guides.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License.
