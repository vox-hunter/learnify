# Authentication API Contract

## POST /api/auth/login

Authenticate user with email and password.

### Request
**Content-Type**: `application/json`

**Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Body Parameters**:
- `email` (required): User email address
  - Type: String (email format)
  - Max length: 255 characters
- `password` (required): User password
  - Type: String
  - Min length: 8 characters

### Response

**Success (200 OK)**:
```json
{
  "user": {
    "id": "user_123456",
    "email": "user@example.com", 
    "name": "John Doe",
    "isGuest": false,
    "createdAt": "2025-01-15T10:30:00Z"
  },
  "session": {
    "id": "session_abc123",
    "token": "jwt_token_here",
    "expiresAt": "2025-09-29T12:00:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Missing credentials:
```json
{
  "error": "missing_credentials", 
  "message": "Email and password are required",
  "details": {
    "missingFields": ["email", "password"]
  }
}
```

**401 Unauthorized** - Invalid credentials:
```json
{
  "error": "invalid_credentials",
  "message": "Invalid email or password",
  "details": {
    "attemptCount": 3,
    "maxAttempts": 5
  }
}
```

**429 Too Many Requests** - Rate limited:
```json
{
  "error": "rate_limited",
  "message": "Too many login attempts",
  "details": {
    "retryAfter": 300,
    "maxAttempts": 5
  }
}
```

---

## POST /api/auth/logout

Logout current user session.

### Request
**Headers**:
- `Authorization`: Bearer {token}

### Response

**Success (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses**:

**401 Unauthorized** - Invalid token:
```json
{
  "error": "invalid_token",
  "message": "Authentication token is invalid or expired"
}
```

---

## GET /api/auth/me

Get current user information.

### Request
**Headers**:
- `Authorization`: Bearer {token}

### Response

**Success (200 OK)**:
```json
{
  "user": {
    "id": "user_123456",
    "email": "user@example.com",
    "name": "John Doe", 
    "isGuest": false,
    "guestUsageCount": 0,
    "guestUsageLimit": 3,
    "lastLoginAt": "2025-09-28T12:00:00Z",
    "createdAt": "2025-01-15T10:30:00Z"
  },
  "session": {
    "id": "session_abc123",
    "expiresAt": "2025-09-29T12:00:00Z"
  }
}
```

**Error Responses**:

**401 Unauthorized** - No token or invalid:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```