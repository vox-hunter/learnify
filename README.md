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
   streamlit run main.py
   ```

## File Structure

- `main.py`: Entry point for the application
- `frontend.py`: User interface implementation
- `local_backend.py`: Backend processing and AI integration
- `prompt.txt`: Prompt template for the AI
- `sys_ins.txt`: System instructions for the AI
- `st_fill_in_the_blanks/`: Custom Streamlit component for fill-in-the-blank questions

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

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License.
