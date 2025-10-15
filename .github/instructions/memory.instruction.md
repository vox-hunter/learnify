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
- Refactoring file upload flow: Removing /course/generate/upload endpoint, routing all uploads through chat/message for AI-driven course generation decisions

## Notes

## UI/Avatar Update (Oct 2025)
- AI logo avatar in ChatView.vue: border removed, logo size increased, aligned with text
- Logo path standardized to /STITCH.png for all usages (header, messages, loading)
- All build and lint checks pass, only warnings remain

## Current Error Fix Task
Critical errors identified:
1. Recursive _log_error function in mongo_auth.py (line 52)
2. pymongo.errors import issues throughout backend
3. Database attribute access on None when connection fails
4. OAuth redirect URI type mismatch
5. Missing optional dependencies (pandas, streamlit)

Fix Progress:
- [x] Fix recursive _log_error function
- [x] Fix pymongo errors import  
- [x] Fix database None attribute access (protected by _ensure_connection checks)
- [x] Fix OAuth type mismatch
- [x] Install missing dependencies
- [x] Verify all errors resolved

## Results:
- All critical runtime errors have been fixed
- FastAPI backend imports and runs successfully
- Vue frontend builds successfully without errors
- Remaining errors are static analysis false positives
- Linting shows only minor warnings, no errors
