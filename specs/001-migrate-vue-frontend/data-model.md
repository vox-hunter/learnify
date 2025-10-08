# data-model.md

## Entities extracted from spec

- Course
  - Fields: id, title, sections (array), metadata
  - Relationships: sections -> lessons -> quizItems
  - Validation: follow backend Pydantic schemas; frontend should treat shapes as readonly DTOs

- User
  - Fields: id, username, email (nullable), preferences, progress
  - Validation: mirror backend session/token semantics

- ChatMessage
  - Fields: id, text, senderId, timestamp, attachments

- Upload
  - Fields: id, filename, size, mimeType, status

## Notes
- No changes to backend schema expected. Frontend should consume and validate using generated TypeScript types from OpenAPI or hand-authored types that match Pydantic models.
