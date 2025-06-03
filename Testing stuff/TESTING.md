# Testing Guide for AI Quiz and Course Generator

## Quick Test

To quickly verify the application is working:

1. **Start the application:**
   ```bash
   streamlit run main.py
   ```

2. **Test with a sample PDF URL:**
   - Use the "Provide URL" option
   - Try this sample educational PDF: `https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf`
   - Or use any educational PDF URL you have access to

3. **Test with file upload:**
   - Use the "Upload File" option
   - Upload any PDF document (max 20MB)

## Component Testing

### 1. Multiple Choice Questions
- Verify radio buttons appear
- Check that selection triggers immediate feedback
- Ensure score updates correctly

### 2. Fill-in-the-Blank Questions
- Custom component should display interactive blanks
- Typing should work in the blank spaces
- Answers should be validated correctly

### 3. Short Answer Questions
- Text area should appear for longer responses
- Case-insensitive matching should work

### 4. True/False Questions
- Radio buttons with True/False options
- Boolean logic should work correctly

### 5. Matching Questions
- Dropdown selections for each item
- "Check Matches" button functionality
- Visual feedback with correct/incorrect indicators

## Error Testing

### API Key Issues
1. Remove or modify the `GEMINI_API_KEY` in `.env`
2. Try to generate a course
3. Should show clear error message about API key

### Invalid PDF Testing
1. Try uploading a non-PDF file (rename a .txt file to .pdf)
2. Should show validation error

### Large File Testing
1. Try uploading a file larger than 20MB
2. Should show file size error

### Network Issues
1. Provide an invalid URL
2. Should show network/download error

## Performance Testing

### Memory Usage
- Test with large PDF files (close to 20MB limit)
- Monitor memory usage during course generation

### Response Time
- Simple PDFs: Should complete in 15-30 seconds
- Complex PDFs: May take 30-60 seconds
- Timeout after 2-3 minutes indicates an issue

## Browser Compatibility

Test in different browsers:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Common Issues and Solutions

### 1. Custom Component Not Loading
**Problem:** Fill-in-the-blank questions show placeholder text instead of interactive input

**Solution:**
```bash
cd st_fill_in_the_blanks/frontend
npm install
npm run build
```

### 2. API Quota Exceeded
**Problem:** Error messages about quota limits

**Solution:**
- Check your Google AI Studio quota
- Wait for quota reset
- Consider upgrading your API plan

### 3. Streamlit Not Found
**Problem:** `streamlit: command not found`

**Solution:**
```bash
pip install streamlit
```

### 4. Import Errors
**Problem:** Missing Python packages

**Solution:**
```bash
pip install -r requirements.txt
```

## Manual Testing Checklist

- [ ] Application starts without errors
- [ ] File upload works
- [ ] URL input works
- [ ] Course generation completes successfully
- [ ] All question types render correctly
- [ ] Scoring system works
- [ ] Navigation between sections works
- [ ] Error messages are clear and helpful
- [ ] Custom component (fill-in-the-blank) works
- [ ] Session state persists during navigation
- [ ] Browser refresh doesn't break the application

## Automated Setup Testing

Run the setup script to test the complete installation:

```bash
python setup.py
```

This will:
- Install all dependencies
- Verify the .env file
- Build the custom component
- Check that everything is working

## Troubleshooting

### Debug Mode
To enable debug logging, modify `local_backend.py`:
```python
DEBUG_MODE = True
```

### Logs Location
Streamlit logs appear in the terminal where you ran `streamlit run main.py`

### Component Issues
If the custom component isn't working:
1. Check that `st_fill_in_the_blanks/frontend/build/` exists
2. Rebuild with `npm run build`
3. Restart the Streamlit application

### Memory Issues
For large PDFs or many questions:
- Monitor system memory usage
- Consider reducing PDF size
- Restart the application if it becomes sluggish
