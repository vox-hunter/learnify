# Document Upload API Contract

## POST /api/documents/upload

Upload a PDF file for course generation.

### Request
**Content-Type**: `multipart/form-data`

**Body Parameters**:
- `file` (required): PDF file to upload
  - Type: File
  - Max size: 20MB
  - Allowed formats: PDF only
- `filename` (optional): Override filename
  - Type: String
  - Max length: 255 characters

### Response

**Success (201 Created)**:
```json
{
  "id": "doc_123456",
  "name": "example.pdf",
  "type": "pdf",
  "size": 2048576,
  "status": "uploaded",
  "uploadedAt": "2025-09-28T12:00:00Z"
}
```

**Error Responses**:

**400 Bad Request** - Invalid file:
```json
{
  "error": "invalid_file",
  "message": "File must be a valid PDF",
  "details": {
    "filename": "example.txt",
    "actualType": "text/plain",
    "expectedType": "application/pdf"
  }
}
```

**413 Payload Too Large** - File too large:
```json
{
  "error": "file_too_large",
  "message": "File size exceeds 20MB limit",
  "details": {
    "fileSize": 25165824,
    "maxSize": 20971520
  }
}
```

**422 Unprocessable Entity** - File validation failed:
```json
{
  "error": "validation_failed",
  "message": "PDF file appears to be corrupted or empty",
  "details": {
    "validationErrors": ["Invalid PDF header", "File size too small"]
  }
}
```