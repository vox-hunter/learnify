# Learnify - AI Course Generator

A simplified, single-file HTML application that generates personalized learning courses from your uploaded materials using AI.

## 🎯 Overview

Learnify transforms your notes, documents, and learning materials into interactive courses with AI-generated content and quizzes. Built as a simple HTML file with no backend dependencies - just open and use!

## ✨ Features

- **Drag & Drop Upload**: Support for PDF, Word docs, text files, and more
- **AI Course Generation**: Powered by Google's Gemini AI
- **Interactive Quizzes**: Multiple choice questions with instant feedback
- **Beautiful UI**: Modern dark theme with glass morphism design
- **Section Navigation**: Progress through course sections at your own pace
- **No Installation**: Single HTML file - works in any modern browser
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

1. **Get a Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key

2. **Setup**
   - Download `learnify.html`
   - Open the file in a text editor
   - Find the `GEMINI_API_KEY` variable and add your API key:
     ```javascript
     const GEMINI_API_KEY = "your_api_key_here";
     ```

3. **Use**
   - Open `learnify.html` in your web browser
   - Upload your learning materials
   - Click "Generate Course"
   - Learn through your personalized course!

## 📚 How It Works

1. **Upload**: Drag and drop your files or click to browse
2. **Generate**: AI processes your content and creates structured course sections
3. **Learn**: Navigate through sections, answer questions, get instant feedback
4. **Progress**: Track your learning journey section by section

## 🎨 Screenshots

### Upload Interface
Clean, intuitive file upload with drag-and-drop support

### Generated Course
Beautiful course interface with sections, content, and interactive quizzes

### Interactive Learning
Answer questions and get immediate feedback with explanations

## 🛠 Technical Details

- **Frontend Only**: Pure HTML, CSS, and JavaScript
- **AI Integration**: Direct integration with Google's Gemini API
- **File Processing**: Client-side file reading and content extraction
- **Responsive**: Tailwind CSS for modern, responsive design
- **No Dependencies**: Self-contained single file

## 📁 File Structure

```
learnify.html          # Complete application in a single file
├── HTML structure     # Page layout and components
├── CSS styling        # Modern dark theme with animations
└── JavaScript logic   # File handling, AI integration, course display
```

## 🎓 Supported File Types

- **Documents**: PDF, Word (.doc, .docx)
- **Text Files**: .txt, .md (Markdown)
- **And more**: The app attempts to read any text-based content

## 🔧 Customization

The app is designed to be easily customizable:

- **Themes**: Modify CSS variables for different color schemes
- **AI Prompts**: Adjust the course generation prompts for different styles
- **Question Types**: Extend the quiz system with new question formats
- **File Support**: Add support for additional file types

## 🌟 Legacy Python Version

The `Quiz_app/` directory contains the previous complex Python/Streamlit implementation with MongoDB integration, user authentication, and advanced features. The new simplified version achieves the core functionality with zero complexity.

## 🤝 Contributing

Feel free to contribute:
- Report bugs or suggest features via GitHub issues
- Submit pull requests for improvements
- Share your customizations and use cases

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Simple. Powerful. Educational.** 🧠✨
