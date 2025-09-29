# URL Document API Contract

## POST /api/documents/url

Submit a URL to a PDF document for course generation.

### Request
**Content-Type**: `application/json`

**Body**:
```json
{
  "url": "https://example.com/document.pdf",
  "filename": "custom-name.pdf"
}
```

**Body Parameters**:
- `url` (required): URL to PDF document
  - Type: String (URL)
  - Must start with http:// or https://
  - Must point to accessible PDF file
- `filename` (optional): Custom filename
  - Type: String
  - Max length: 255 characters

### Response

**Success (201 Created)**:
```json
{
  "id": "doc_789012",
  "name": "document.pdf",
  "type": "url",
  "content": "https://example.com/document.pdf",
  "status": "processing",
  "uploadedAt": "2025-09-28T12:00:00Z"
}
```

**Error Responses**:

**400 Bad Request** - Invalid URL:
```json
{
  "error": "invalid_url",
  "message": "URL must start with http:// or https://",
  "details": {
    "providedUrl": "ftp://example.com/doc.pdf",
    "validFormats": ["http://", "https://"]
  }
}
```

**404 Not Found** - URL not accessible:
```json
{
  "error": "url_not_found",
  "message": "Unable to access the provided URL",
  "details": {
    "url": "https://example.com/missing.pdf",
    "httpStatus": 404
  }
}
```

**422 Unprocessable Entity** - Not a PDF:
```json
{
  "error": "invalid_content_type",
  "message": "URL does not point to a PDF file",
  "details": {
    "detectedType": "text/html",
    "expectedType": "application/pdf"
  }
}
```