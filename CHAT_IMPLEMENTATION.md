# AI Loom Chat System Implementation

## Overview
This implementation adds a real-time chat interface to AI Loom that replaces the old file/URL upload tabs with a unified conversational interface powered by Google Gemini SDK's multi-turn chat API.

## Architecture

### Backend Components

#### 1. Chat Session Manager (`backend/chat_manager.py`)
**Purpose**: Manages multi-turn conversations using Gemini SDK's built-in chat functionality.

**Key Features**:
- Creates and manages chat sessions using `client.chats.create()`
- No manual conversation history tracking (SDK handles it)
- Supports file uploads and URL context automatically
- Integrated tools: URL Context and Google Search

**Core Methods**:
```python
# Create new chat session
session_id, chat = chat_manager.create_session(system_instruction)

# Send message with optional file/URL
result = chat_manager.send_message(
    session_id=session_id,
    message="Hello!",
    file_data=bytes,
    file_mime_type="application/pdf",
    url="https://example.com"
)
```

**Tools Enabled**:
- `url_context`: Automatically fetches and analyzes URLs (up to 20 per request)
- `google_search`: Provides real-time information via Google Search

#### 2. FastAPI Endpoints (`api/main.py`)

**POST /chat/message**
- **Input**: FormData with `message`, optional `session_id`, `file`, `url`
- **Processing**: 
  1. Validates file security if file uploaded
  2. Calls `chat_manager.send_message()` with all context
  3. Returns AI reply and session_id
- **Output**: `{ success: bool, reply: str, session_id: str }`

**GET /chat/history/{session_id}**
- Retrieves conversation history for a session
- Uses SDK's `chat.get_history()` method

**DELETE /chat/session/{session_id}**
- Deletes a chat session and clears history

### Frontend Components

#### 1. ChatView Component (`vue-frontend/src/views/ChatView.vue`)

**UI Structure**:
```
┌─────────────────────────────────┐
│ Header (Logo, Title)            │
├─────────────────────────────────┤
│                                 │
│ Chat Feed (Scrollable)          │
│  - Welcome Message              │
│  - User Messages (right-aligned)│
│  - AI Messages (left-aligned)   │
│  - Typing Indicator             │
│                                 │
├─────────────────────────────────┤
│ Input Area                      │
│  [📎][🔗] [Message Input] [🚀]  │
└─────────────────────────────────┘
```

**State Management**:
- `messages`: Array of chat messages
- `sessionId`: Stored in localStorage for persistence
- `messageInput`: Current text input
- `selectedFile`: File to upload
- `urlInput`: URL to analyze

**Key Features**:
- Drag & drop file support
- URL input toggle
- Auto-scroll to new messages
- Markdown-style citation links (e.g., `[1](url)`)
- Typing indicator during AI processing
- Example prompts for new users

#### 2. Session Persistence
```javascript
// On mount: Load existing session
const savedSessionId = localStorage.getItem('chat_session_id')

// After each message: Save session ID
localStorage.setItem('chat_session_id', sessionId.value)
```

## Data Flow

### 1. Simple Text Message
```
User types "Hello" → Vue sends POST /chat/message → 
Backend creates/retrieves session → Gemini SDK processes → 
AI reply returned → Vue displays in chat feed
```

### 2. File Upload Flow
```
User selects file → Vue reads file as FormData → 
Backend validates file security → Converts to bytes → 
Gemini SDK uploads via File API → Processes content → 
AI analyzes file → Reply with file insights
```

### 3. URL Analysis Flow
```
User pastes URL → Vue sends with message → 
Backend includes URL in request → Gemini SDK's url_context tool → 
Fetches URL content automatically → AI analyzes → 
Reply with URL insights + citations
```

### 4. Multi-turn Conversation
```
Message 1: User asks about Python
  ↓ session_id = "abc123" created
Response 1: AI explains Python basics
  ↓ session_id stored in localStorage

Message 2: "Can you explain variables?" + session_id
  ↓ Backend retrieves existing chat object
Response 2: AI remembers context, explains variables
```

## Gemini SDK Integration Details

### Chat Creation
```python
chat = client.chats.create(
    model="gemini-2.0-flash-exp",  # Latest model with URL context
    config=GenerateContentConfig(
        system_instruction="You are AI Loom...",
        tools=[
            {"url_context": {}},    # Enable URL fetching
            {"google_search": {}}   # Enable web search
        ],
        temperature=0.7
    )
)
```

### Sending Messages with Files
```python
# Prepare file part
file_part = types.Part.from_bytes(
    data=file_data,
    mime_type="application/pdf"
)

# Send with message
response = chat.send_message([
    "Analyze this document",
    file_part
])
```

### URL Context Tool Usage
When a URL is included in the message:
1. Gemini SDK's `url_context` tool automatically fetches the URL
2. Content is extracted (supports HTML, PDF, images)
3. AI analyzes content in context of the conversation
4. Response includes `url_context_metadata` with retrieved URLs

### Conversation History
```python
# SDK manages history automatically
history = chat.get_history()

# Returns list of messages:
# [
#   { role: 'user', parts: [...] },
#   { role: 'model', parts: [...] },
#   ...
# ]
```

## Session Management

### In-Memory Session Store
```python
# Simple dict mapping session_id -> chat object
self.sessions: Dict[str, Any] = {}

# Create
self.sessions[session_id] = chat

# Retrieve
chat = self.sessions.get(session_id)

# Delete
del self.sessions[session_id]
```

**Production Considerations**:
- Current implementation stores sessions in memory
- For production, migrate to Redis or database
- Add session expiration/cleanup
- Scale across multiple server instances

## Frontend-Backend Communication

### API Request Format
```javascript
const formData = new FormData()
formData.append('message', 'Hello!')
formData.append('session_id', sessionId)  // Optional
formData.append('file', fileObject)       // Optional
formData.append('url', 'https://...')     // Optional

const response = await api.post('/chat/message', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

### API Response Format
```json
{
  "success": true,
  "reply": "AI response text with [citations](url)",
  "session_id": "uuid-v4-string"
}
```

### Error Handling
```javascript
try {
  const response = await api.post('/chat/message', formData)
  // Handle success
} catch (err) {
  error.value = err.response?.data?.detail || 'Failed to send message'
}
```

## Styling & UX

### Theme Support
- Uses existing CSS variables from `main.css`
- Adapts to light/dark theme automatically
- Gradient accents for primary actions

### Responsive Design
```css
@media (max-width: 768px) {
  .message-content { max-width: 85%; }
  .input-btn { width: 40px; height: 40px; }
}
```

### Animations
- Message slide-in on send
- Typing indicator pulse
- Button hover effects
- Smooth scroll to new messages

## Testing

### Backend Tests
```bash
# Test chat manager import
python -c "from chat_manager import ChatSessionManager; print('OK')"

# Run test script
python test_chat.py
```

### Frontend Tests
1. Open http://localhost:3000
2. Verify chat interface loads
3. Send text message
4. Upload file
5. Paste URL
6. Verify multi-turn conversation

### Integration Tests
1. Send message → verify AI responds
2. Refresh page → verify session persists
3. Upload PDF → verify file processing
4. Paste URL → verify URL context tool fetches content
5. Ask follow-up → verify conversation context maintained

## Deployment Checklist

- [ ] Backend: Add `chat_manager` to imports in `main.py` ✓
- [ ] Backend: Initialize `ChatSessionManager` on startup ✓
- [ ] Backend: Add `/chat/message` endpoint ✓
- [ ] Frontend: Create `ChatView.vue` component ✓
- [ ] Frontend: Update router to use ChatView as home ✓
- [ ] Frontend: Test file upload
- [ ] Frontend: Test URL input
- [ ] Backend: Test Gemini SDK integration
- [ ] End-to-end: Test multi-turn conversation
- [ ] Production: Migrate session store to Redis/DB
- [ ] Production: Add session cleanup/expiration
- [ ] Production: Add rate limiting

## API Reference

### ChatSessionManager

**`__init__()`**
- Initializes Gemini client with API key
- Sets up empty session store

**`create_session(system_instruction: Optional[str]) -> tuple[str, Any]`**
- Creates new chat session with tools enabled
- Returns: (session_id, chat_object)

**`send_message(session_id, message, file_data, file_mime_type, url) -> Dict`**
- Sends message to chat session
- Handles file uploads and URL context
- Returns: { success, reply, session_id, error }

**`get_history(session_id: str) -> Optional[list]`**
- Retrieves conversation history
- Returns: List of messages or None

**`delete_session(session_id: str) -> bool`**
- Removes session from store
- Returns: True if deleted, False if not found

## Troubleshooting

### "Chat service unavailable"
- Check if `ChatSessionManager` initialized in `startup_event()`
- Verify `GEMINI_API_KEY` in `.env` file

### Session not persisting
- Check localStorage in browser DevTools
- Verify `session_id` sent in subsequent requests

### File upload fails
- Check file size < 20MB
- Verify file type in `accept` attribute
- Check `file_security.py` validation

### URL context not working
- Verify URL is publicly accessible (no auth)
- Check `url_context` tool enabled in config
- Ensure model is `gemini-2.0-flash-exp` or later

## Future Enhancements

1. **Streaming Responses**: Use `send_message_stream()` for real-time text
2. **Voice Input**: Add speech-to-text integration
3. **Image Generation**: Integrate Imagen for visual content
4. **Code Execution**: Add code_execution tool for live demos
5. **Shareable Chats**: Export/import conversation history
6. **Chat Templates**: Pre-built prompts for common tasks
7. **Analytics**: Track usage, popular topics, session duration

## References

- [Gemini Text Generation Docs](https://ai.google.dev/gemini-api/docs/text-generation)
- [URL Context Tool](https://ai.google.dev/gemini-api/docs/url-context)
- [Google Search Tool](https://ai.google.dev/gemini-api/docs/google-search)
- [Shadcn Vue Input Components](https://www.shadcn-vue.com/docs/components/input.html)
