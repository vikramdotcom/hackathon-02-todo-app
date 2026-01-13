# REST API Endpoints

**Feature**: Phase II – Full-Stack Web Application
**Date**: 2026-01-10
**Base URL**: `/api/v1`

## Overview

This document defines all REST API endpoints for Phase II. All endpoints follow RESTful conventions and return JSON responses. Protected endpoints require JWT authentication token in the Authorization header.

## Authentication Endpoints

### POST /auth/register

**Purpose**: Register a new user account

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Request Validation**:
- email: Required, valid email format, unique
- username: Required, 3-50 characters, alphanumeric plus underscore/hyphen, unique
- password: Required, 8+ characters, at least one uppercase, one lowercase, one number

**Success Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-01-10T12:00:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid input or validation failure
- 409 Conflict: Email or username already exists

---

### POST /auth/login

**Purpose**: Authenticate user and receive JWT token

**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

**Error Responses**:
- 400 Bad Request: Missing email or password
- 401 Unauthorized: Invalid credentials

---

### POST /auth/logout

**Purpose**: Invalidate current JWT token (client-side token removal)

**Authentication**: Required (Bearer token)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token

---

### GET /auth/me

**Purpose**: Get current authenticated user information

**Authentication**: Required (Bearer token)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T12:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token

---

## Todo Endpoints

### GET /todos

**Purpose**: List all todos for authenticated user with optional filtering

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `status`: Filter by completion status (completed, pending, all) - default: all
- `priority`: Filter by priority (low, medium, high, all) - default: all
- `tag`: Filter by tag (exact match) - optional
- `search`: Search in title and description (case-insensitive) - optional
- `limit`: Number of results per page (1-100) - default: 50
- `offset`: Number of results to skip - default: 0
- `sort_by`: Sort field (created_at, updated_at, due_date, priority, title) - default: created_at
- `sort_order`: Sort direction (asc, desc) - default: desc

**Success Response** (200 OK):
```json
{
  "todos": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive docs for Phase II",
      "completed": false,
      "priority": "high",
      "tags": ["work", "documentation"],
      "due_date": "2026-01-15T17:00:00Z",
      "recurrence": null,
      "created_at": "2026-01-10T12:00:00Z",
      "updated_at": "2026-01-10T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 400 Bad Request: Invalid query parameters

---

### GET /todos/{id}

**Purpose**: Get a specific todo by ID

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T12:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user

---

### POST /todos

**Purpose**: Create a new todo

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null
}
```

**Request Validation**:
- title: Required, 1-10,000 characters
- description: Optional, 0-10,000 characters, default: ""
- priority: Optional, one of (low, medium, high), default: "medium"
- tags: Optional, array of strings, max 20 tags, default: []
- due_date: Optional, valid ISO 8601 datetime, default: null
- recurrence: Optional, string, default: null

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T12:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 400 Bad Request: Invalid input or validation failure

---

### PUT /todos/{id}

**Purpose**: Update an existing todo (full update)

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Request Body**:
```json
{
  "title": "Complete project documentation - Updated",
  "description": "Write comprehensive docs for Phase II with examples",
  "priority": "medium",
  "tags": ["work", "documentation", "examples"],
  "due_date": "2026-01-16T17:00:00Z",
  "recurrence": "weekly"
}
```

**Request Validation**:
- Same as POST /todos
- All fields required (full update)
- Cannot update: id, user_id, created_at

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation - Updated",
  "description": "Write comprehensive docs for Phase II with examples",
  "completed": false,
  "priority": "medium",
  "tags": ["work", "documentation", "examples"],
  "due_date": "2026-01-16T17:00:00Z",
  "recurrence": "weekly",
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T14:30:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user
- 400 Bad Request: Invalid input or validation failure

---

### PATCH /todos/{id}

**Purpose**: Partially update an existing todo

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "priority": "low"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated title",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "low",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T15:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user
- 400 Bad Request: Invalid input or validation failure

---

### DELETE /todos/{id}

**Purpose**: Delete a todo

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Success Response** (204 No Content):
No response body

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user

---

### PATCH /todos/{id}/complete

**Purpose**: Mark a todo as complete

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": true,
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T16:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user

---

### PATCH /todos/{id}/incomplete

**Purpose**: Mark a todo as incomplete

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `id`: Todo ID (integer)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-01-15T17:00:00Z",
  "recurrence": null,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T16:30:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Todo not found or doesn't belong to user

---

## User Endpoints

### GET /users/me

**Purpose**: Get current user profile (same as GET /auth/me)

**Authentication**: Required (Bearer token)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T12:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token

---

### PUT /users/me

**Purpose**: Update current user profile

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "username": "john_doe_updated",
  "email": "newemail@example.com"
}
```

**Request Validation**:
- username: Optional, 3-50 characters, alphanumeric plus underscore/hyphen, unique
- email: Optional, valid email format, unique

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "john_doe_updated",
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T17:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token
- 400 Bad Request: Invalid input or validation failure
- 409 Conflict: Email or username already exists

---

### GET /users/me/stats

**Purpose**: Get user statistics (todo counts, completion rate)

**Authentication**: Required (Bearer token)

**Success Response** (200 OK):
```json
{
  "total_todos": 25,
  "completed_todos": 15,
  "pending_todos": 10,
  "completion_rate": 60.0,
  "todos_by_priority": {
    "high": 5,
    "medium": 12,
    "low": 8
  },
  "todos_created_this_week": 3,
  "todos_completed_this_week": 2
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or expired token

---

## Common Response Formats

### Success Response Structure

All successful responses follow this structure:
```json
{
  "data": { /* response data */ },
  "message": "Optional success message"
}
```

For list endpoints:
```json
{
  "data": [ /* array of items */ ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Error Response Structure

All error responses follow this structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* optional additional details */ }
  }
}
```

### HTTP Status Codes

- **200 OK**: Successful GET, PUT, PATCH request
- **201 Created**: Successful POST request (resource created)
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid input or validation failure
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Valid token but insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (duplicate email/username)
- **422 Unprocessable Entity**: Validation error with detailed field errors
- **500 Internal Server Error**: Server error

## Authentication

### JWT Token Format

**Header**:
```
Authorization: Bearer <token>
```

**Token Payload**:
```json
{
  "sub": "1",
  "email": "user@example.com",
  "exp": 1704988800
}
```

**Token Expiration**: 24 hours (86400 seconds)

### Token Refresh

Phase II does not implement token refresh. Users must re-authenticate after token expiration. Token refresh can be added in future phases if needed.

## Rate Limiting

**Authentication Endpoints**:
- 5 requests per minute per IP address
- Prevents brute force attacks

**Other Endpoints**:
- 100 requests per minute per authenticated user
- Prevents abuse and ensures fair usage

## CORS Configuration

**Allowed Origins**:
- Development: http://localhost:3000
- Production: https://yourdomain.com

**Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

## API Versioning

**Current Version**: v1

**Version Strategy**: URL-based versioning (/api/v1/)

**Future Versions**: Breaking changes will increment version (v2, v3, etc.)

## Conclusion

All API endpoints follow RESTful conventions, provide consistent response formats, and include proper authentication and validation. The API is designed to be consumed by the Next.js frontend and future Phase III AI agents.

**Status**: ✅ API contracts complete
