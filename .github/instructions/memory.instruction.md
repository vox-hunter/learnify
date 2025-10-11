---
applyTo: '**'
---

# User Memory

## User Preferences
- Programming languages: JavaScript, TypeScript, Python
- Code style preferences: Clean, modular, best practices, Vue 3 conventions
- Development environment: VS Code, Windows, PowerShell
- Communication style: Concise, professional, minimal explanations

## Project Context
- Current project type: AI-powered course and quiz generator web app
- Tech stack: Vue 3 + Vite + Pinia + FastAPI + MongoDB + Gemini AI
- Architecture patterns: SPA, REST API, modular state management
- Key requirements: Robust Markdown + LaTeX rendering in chat, security, scalability

## Coding Patterns
- Preferred patterns and practices: Use official libraries, sanitize HTML, test edge cases
- Code organization preferences: Component-based, separation of concerns
- Testing approaches: Manual and automated, edge case coverage
- Documentation style: Inline comments, minimal external docs

## Context7 Research History
- Libraries researched: markdown-it, markdown-it-katex, katex
- Best practices: Use markdown-it-katex for math, import KaTeX CSS, configure delimiters, sanitize output
- Implementation patterns: Vue 3 v-html rendering, DOMPurify, markdown-it plugin chaining
- Version-specific findings: KaTeX 0.16+, markdown-it-katex latest

## Conversation History
- Implemented robust Markdown + LaTeX rendering in chat
- Previous attempt rendered math incorrectly; now uses markdown-it-katex
- All steps completed and tested
- **Current Task**: Transform chat into persistent, course-linked, context-aware system with chat history, resuming, and dynamic interaction

## Current Implementation Task
**Status**: ✅ COMPLETED

**Goal**: Persistent chat system with course linking, history, and resume capability

### Completed Features:
1. ✅ Backend MongoDB chat persistence
   - Created `mongo_chat_manager.py` with full CRUD operations
   - Chat schema supports user ownership, course linking, messages array
   - Indexes created for efficient querying
   
2. ✅ Backend API endpoints
   - POST `/chats/create` - Create new chat
   - GET `/chats/user/{username}` - Get all user chats
   - GET `/chats/{chat_id}` - Get specific chat
   - GET `/chats/course/{username}/{course_id}` - Get/create course chat
   - PUT `/chats/{chat_id}/title` - Update chat title
   - DELETE `/chats/{chat_id}` - Soft delete chat
   - Updated POST `/chat/message` to persist messages to MongoDB
   
3. ✅ Frontend chat store (`stores/chat.js`)
   - State management for chats list and current chat
   - Actions for all CRUD operations
   - Integration with API endpoints
   
4. ✅ Updated Sidebar.vue
   - Changed "Chat" to "Chats" with dropdown
   - Lists past chat sessions sorted by updated_at
   - Click to resume chat
   - Shows chat title and relative timestamp
   
5. ✅ Updated ChatView.vue
   - Loads chat from URL query parameter `?chat_id=`
   - Persists messages to MongoDB automatically
   - Resume functionality with history context injection (one-time, silent)
   - Tracks `resumedWithHistory` flag to inject history only once
   - Updates chat store on message send
   
6. ✅ Added Edit buttons to CoursesView.vue
   - Pencil + sparkles icon (✏️✨)
   - Opens course-linked chat
   - Auto-creates chat if doesn't exist
   - Navigates to chat view with course context

### Resume Behavior:
- When resuming a chat, the first message injects full history as context
- History wrapped with `[Previous conversation context...]` prefix
- Gemini receives context but user doesn't see the injection
- Flag `resumedWithHistory` prevents re-injection on subsequent messages

### Course Chat Linking:
- Each course can have dedicated chat thread
- Chat stored with `course_id` field in MongoDB
- Edit button creates/opens course chat
- Course context maintained across sessions
