# Course Status API Contract

## GET /api/courses/status/{jobId}

Check the status of course generation job.

### Request
**Method**: GET
**Path Parameters**:
- `jobId` (required): Course generation job ID
  - Type: String
  - Format: job_[alphanumeric]

### Response

**Success (200 OK)** - Job in progress:
```json
{
  "jobId": "job_abc123", 
  "status": "processing",
  "progress": 45,
  "message": "🤖 AI is analyzing PDF content",
  "estimatedTimeRemaining": "15-20 seconds"
}
```

**Success (200 OK)** - Job completed:
```json
{
  "jobId": "job_abc123",
  "status": "completed", 
  "progress": 100,
  "message": "Course generated successfully",
  "result": {
    "id": "course_456789",
    "title": "Introduction to Machine Learning",
    "description": "A comprehensive course covering ML fundamentals",
    "sections": [
      {
        "id": "section_001",
        "title": "What is Machine Learning?",
        "content": "Machine learning is a subset of artificial intelligence...",
        "order": 1,
        "quiz": {
          "id": "quiz_001",
          "questions": [
            {
              "id": "q_001",
              "type": "multiple-choice",
              "question": "What is machine learning?",
              "options": ["AI subset", "Programming language", "Database", "Operating system"],
              "correctAnswer": "AI subset",
              "points": 10,
              "order": 1
            }
          ],
          "totalPoints": 10,
          "passingScore": 7
        }
      }
    ],
    "totalQuestions": 1,
    "estimatedDuration": 15,
    "createdAt": "2025-09-28T12:05:00Z"
  }
}
```

**Success (200 OK)** - Job failed:
```json
{
  "jobId": "job_abc123",
  "status": "error",
  "progress": 100,
  "message": "Course generation failed",
  "error": {
    "code": "ai_processing_failed",
    "message": "Unable to extract meaningful content from document",
    "details": "Document appears to contain mostly images with no extractable text"
  }
}
```

**Error Responses**:

**404 Not Found** - Invalid job ID:
```json
{
  "error": "job_not_found",
  "message": "Job with specified ID does not exist",
  "details": {
    "jobId": "job_invalid123"
  }
}
```