# Data Model: AI Loom React Frontend

## Core Entities

### Document
**Purpose**: Represents uploaded PDFs or URL-referenced content awaiting processing  
**Fields**:
- `id`: Unique identifier (string)
- `name`: Original filename or URL title (string)
- `type`: Document type ('pdf', 'url') (string)
- `content`: File content or URL (string)
- `status`: Processing status ('uploading', 'processing', 'completed', 'error') (string)
- `uploadedAt`: Upload timestamp (Date)
- `size`: File size in bytes (number, optional for URLs)

**Validation Rules**:
- `name` must be non-empty string
- `type` must be either 'pdf' or 'url'
- `status` must be valid processing state
- PDF files must be under backend size limit
- URLs must be valid HTTP/HTTPS format

**State Transitions**:
```
uploading → processing → completed
uploading → processing → error
```

### Course
**Purpose**: AI-generated learning content with structured sections and quizzes  
**Fields**:
- `id`: Unique course identifier (string)
- `title`: Course title derived from document (string)
- `description`: Brief course description (string)
- `sections`: Array of course sections (Section[])
- `totalQuestions`: Total number of quiz questions (number)
- `estimatedDuration`: Estimated completion time in minutes (number)
- `createdAt`: Course generation timestamp (Date)
- `documentId`: Reference to source document (string)

**Validation Rules**:
- `title` must be non-empty string
- `sections` must contain at least one section
- `totalQuestions` must be positive integer
- `documentId` must reference valid document

**Relationships**:
- Belongs to one Document (1:1)
- Contains multiple Sections (1:N)

### Section
**Purpose**: Individual course section with content and associated quiz  
**Fields**:
- `id`: Unique section identifier (string)
- `title`: Section title (string)
- `content`: Learning content/material (string)
- `order`: Section order within course (number)
- `quiz`: Associated quiz questions (Quiz)
- `courseId`: Reference to parent course (string)

**Validation Rules**:
- `title` must be non-empty string
- `order` must be positive integer, unique within course
- `content` must be non-empty string

**Relationships**:
- Belongs to one Course (N:1)
- Contains one Quiz (1:1)

### Quiz
**Purpose**: Interactive questions with various types and scoring  
**Fields**:
- `id`: Unique quiz identifier (string)
- `questions`: Array of questions (Question[])
- `totalPoints`: Maximum possible points (number)
- `passingScore`: Minimum score to pass (number)
- `sectionId`: Reference to parent section (string)

**Validation Rules**:
- `questions` must contain at least one question
- `totalPoints` must equal sum of question points
- `passingScore` must be between 0 and totalPoints

**Relationships**:
- Belongs to one Section (1:1)
- Contains multiple Questions (1:N)

### Question
**Purpose**: Individual quiz question with type-specific properties  
**Fields**:
- `id`: Unique question identifier (string)
- `type`: Question type ('multiple-choice', 'fill-in-blanks', 'short-answer', 'true-false', 'matching') (string)
- `question`: Question text (string)
- `points`: Points awarded for correct answer (number)
- `options`: Answer options for multiple choice (string[], optional)
- `correctAnswer`: Correct answer or answers (string | string[])
- `explanation`: Explanation for correct answer (string, optional)
- `order`: Question order within quiz (number)

**Validation Rules**:
- `type` must be valid question type
- `question` must be non-empty string
- `points` must be positive number
- `options` required for multiple-choice and matching types
- `correctAnswer` format depends on question type

**Type-Specific Validation**:
- Multiple choice: `options` array with 2-6 items, `correctAnswer` must be in options
- Fill-in-blanks: `correctAnswer` can be string or array for multiple blanks
- True/false: `correctAnswer` must be 'true' or 'false'
- Matching: `options` and `correctAnswer` must be equal-length arrays

### User
**Purpose**: Authenticated user account with session and progress tracking  
**Fields**:
- `id`: Unique user identifier (string)
- `email`: User email address (string)
- `name`: User display name (string, optional)
- `isGuest`: Whether user is in guest mode (boolean)
- `guestUsageCount`: Number of courses generated as guest (number)
- `guestUsageLimit`: Maximum courses allowed as guest (number)
- `lastLoginAt`: Last login timestamp (Date, optional)
- `createdAt`: Account creation timestamp (Date)

**Validation Rules**:
- `email` must be valid email format
- `guestUsageCount` must be non-negative integer
- `guestUsageLimit` must be positive integer

**Relationships**:
- Has multiple Sessions (1:N)
- Has multiple Progress records (1:N)

### Session
**Purpose**: User authentication state and temporary data  
**Fields**:
- `id`: Unique session identifier (string)
- `userId`: Reference to user account (string, optional for guests)
- `token`: Authentication token (string, optional)
- `isAuthenticated`: Authentication status (boolean)
- `expiresAt`: Session expiration timestamp (Date)
- `createdAt`: Session creation timestamp (Date)
- `lastActivityAt`: Last activity timestamp (Date)

**Validation Rules**:
- `token` required if `isAuthenticated` is true
- `expiresAt` must be in the future for active sessions
- Guest sessions must have limited lifetime

**State Transitions**:
```
created → authenticated → expired
created → expired (guest sessions)
```

### Progress
**Purpose**: User progress tracking across courses and sections  
**Fields**:
- `id`: Unique progress identifier (string)
- `userId`: Reference to user account (string)
- `courseId`: Reference to course (string)
- `sectionId`: Current section being attempted (string, optional)
- `completedSections`: Array of completed section IDs (string[])
- `currentScore`: Current accumulated score (number)
- `totalPossibleScore`: Total possible score for completed sections (number)
- `completionPercentage`: Course completion percentage (number)
- `startedAt`: When user started the course (Date)
- `lastActivityAt`: Last activity timestamp (Date)
- `completedAt`: Course completion timestamp (Date, optional)

**Validation Rules**:
- `currentScore` must be non-negative
- `totalPossibleScore` must be positive if completedSections not empty
- `completionPercentage` must be between 0 and 100
- `completedSections` must contain valid section IDs

**Relationships**:
- Belongs to one User (N:1)
- References one Course (N:1)
- References one Section (current) (N:1, optional)

## Data Flow Patterns

### Course Generation Flow
```
Document (uploaded) → Backend Processing → Course (generated) → Sections → Quizzes
```

### User Progress Flow
```
User → Session (auth) → Course (start) → Progress (tracking) → Section (complete) → Progress (update)
```

### Guest Usage Flow
```
Guest → Session (temporary) → Usage Count Check → Course Generation (if within limits)
```

## Frontend State Management

### Global State (React Context)
- Current user session
- Authentication status
- Theme preferences
- Alert/notification state

### Server State (React Query)
- Document upload status
- Course data
- User progress
- Authentication tokens

### Local Component State
- Form input values
- UI interaction state
- Loading/error states
- Quiz answer selections