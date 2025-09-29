# Course Generation API Contract

## POST /api/courses/generate

Generate a course from an uploaded document.

### Request
**Content-Type**: `application/json`

**Body**:
```json
{
  "documentId": "doc_123456"
}
```

**Body Parameters**:
- `documentId` (required): ID of uploaded document
  - Type: String
  - Must reference valid uploaded document

### Response

**Success (202 Accepted)**:
```json
{
  "jobId": "job_abc123",
  "status": "queued",
  "message": "Course generation started",
  "estimatedDuration": "30-60 seconds"
}
```

**Error Responses**:

**400 Bad Request** - Invalid document ID:
```json
{
  "error": "invalid_document_id",
  "message": "Document ID is required",
  "details": {
    "field": "documentId",
    "issue": "missing_required_field"
  }
}
```

**404 Not Found** - Document not found:
```json
{
  "error": "document_not_found",
  "message": "Document with specified ID does not exist",
  "details": {
    "documentId": "doc_invalid123"
  }
}
```

**409 Conflict** - Document already processing:
```json
{
  "error": "document_processing",
  "message": "Course generation already in progress for this document",
  "details": {
    "documentId": "doc_123456",
    "existingJobId": "job_xyz789",
    "status": "processing"
  }
}
```

**422 Unprocessable Entity** - Document validation failed:
```json
{
  "error": "document_invalid",
  "message": "Document failed validation and cannot be processed",
  "details": {
    "documentId": "doc_123456",
    "validationErrors": ["File corrupted", "Content too short"]
  }
}
```