# Phase V API Reference

## Overview

The Phase V Todo Chatbot API provides RESTful endpoints for managing todos with advanced features including recurring tasks, due dates, priorities, tags, and reminders.

**Base URL**: `http://localhost:8000/api/v2`

**Authentication**: Bearer token (to be implemented)

**Content Type**: `application/json`

## Endpoints

### Health & Status

#### GET /health
Check overall application health.

**Response**: 200 OK
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "api": "healthy"
  },
  "version": "2.0.0"
}
```

#### GET /ready
Kubernetes readiness probe.

**Response**: 200 OK
```json
{
  "status": "ready"
}
```

#### GET /live
Kubernetes liveness probe.

**Response**: 200 OK
```json
{
  "status": "alive"
}
```

---

## Todo Endpoints

### POST /api/v2/todos
Create a new todo.

**Request Body**:
```json
{
  "title": "Weekly team standup",
  "description": "Discuss progress and blockers",
  "due_date": "2026-02-18T09:00:00Z",
  "priority": "high",
  "tags": ["work", "meetings"],
  "reminder_offsets": [1440, 60]
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "title": "Weekly team standup",
  "description": "Discuss progress and blockers",
  "completed": false,
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:00:00Z",
  "user_id": 1,
  "due_date": "2026-02-18T09:00:00Z",
  "priority": "high",
  "tags": ["work", "meetings"],
  "recurrence_pattern_id": null,
  "reminder_offsets": [1440, 60],
  "is_overdue": false,
  "is_recurring": false,
  "has_reminders": true
}
```

### GET /api/v2/todos
List todos with filtering.

**Query Parameters**:
- `completed` (boolean): Filter by completion status
- `priority` (string): Filter by priority (low, medium, high, urgent)
- `tags` (array): Filter by tags
- `overdue_only` (boolean): Only return overdue tasks
- `recurring_only` (boolean): Only return recurring tasks
- `limit` (integer): Maximum results (default: 100, max: 1000)
- `offset` (integer): Pagination offset (default: 0)

**Example**: `GET /api/v2/todos?completed=false&priority=high&limit=20`

**Response**: 200 OK
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Weekly team standup",
      "completed": false,
      "priority": "high",
      "is_overdue": false
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### GET /api/v2/todos/{id}
Get a specific todo.

**Path Parameters**:
- `id` (integer): Todo ID

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Weekly team standup",
  "description": "Discuss progress and blockers",
  "completed": false,
  "due_date": "2026-02-18T09:00:00Z",
  "priority": "high",
  "tags": ["work", "meetings"],
  "is_overdue": false,
  "is_recurring": false
}
```

**Error Response**: 404 Not Found
```json
{
  "error": "not_found",
  "message": "Todo with id 999 not found",
  "details": {}
}
```

### PATCH /api/v2/todos/{id}
Update a todo.

**Path Parameters**:
- `id` (integer): Todo ID

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": false,
  "due_date": "2026-02-20T09:00:00Z",
  "priority": "urgent",
  "tags": ["work", "urgent"]
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Updated title",
  "updated_at": "2026-02-11T11:00:00Z"
}
```

### POST /api/v2/todos/{id}/complete
Mark a todo as completed. If recurring, creates next instance.

**Path Parameters**:
- `id` (integer): Todo ID

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Weekly team standup",
  "completed": true,
  "updated_at": "2026-02-11T11:00:00Z"
}
```

### DELETE /api/v2/todos/{id}
Delete a todo.

**Path Parameters**:
- `id` (integer): Todo ID

**Response**: 204 No Content

### POST /api/v2/todos/search
Search todos by title and description.

**Request Body**:
```json
{
  "query": "meeting",
  "limit": 50
}
```

**Response**: 200 OK
```json
[
  {
    "id": 1,
    "title": "Weekly team standup",
    "description": "Discuss progress and blockers"
  }
]
```

### GET /api/v2/todos/overdue/list
Get all overdue todos.

**Response**: 200 OK
```json
[
  {
    "id": 2,
    "title": "Overdue task",
    "due_date": "2026-02-10T09:00:00Z",
    "is_overdue": true
  }
]
```

### GET /api/v2/todos/upcoming/list
Get upcoming todos.

**Query Parameters**:
- `days_ahead` (integer): Days to look ahead (default: 7, max: 365)

**Example**: `GET /api/v2/todos/upcoming/list?days_ahead=14`

**Response**: 200 OK
```json
[
  {
    "id": 1,
    "title": "Weekly team standup",
    "due_date": "2026-02-18T09:00:00Z"
  }
]
```

---

## Recurrence Pattern Endpoints

### POST /api/v2/recurrence-patterns
Create a recurrence pattern.

**Request Body**:
```json
{
  "frequency": "weekly",
  "interval": 1,
  "end_condition": "never",
  "days_of_week": [0, 2, 4]
}
```

**Frequency Options**: `daily`, `weekly`, `monthly`, `yearly`, `custom`

**End Condition Options**: `never`, `after_occurrences`, `by_date`

**Response**: 201 Created
```json
{
  "id": 1,
  "frequency": "weekly",
  "interval": 1,
  "end_condition": "never",
  "next_occurrence": "2026-02-18T09:00:00Z",
  "occurrence_count": 0,
  "days_of_week": [0, 2, 4]
}
```

### GET /api/v2/recurrence-patterns/{id}
Get a recurrence pattern.

**Path Parameters**:
- `id` (integer): Pattern ID

**Response**: 200 OK

### PATCH /api/v2/recurrence-patterns/{id}
Update a recurrence pattern.

**Request Body** (all fields optional):
```json
{
  "interval": 2,
  "end_condition": "after_occurrences",
  "end_after_occurrences": 10
}
```

**Response**: 200 OK

### DELETE /api/v2/recurrence-patterns/{id}
Delete a recurrence pattern.

**Response**: 204 No Content

### GET /api/v2/recurrence-patterns/active/list
Get all active recurrence patterns.

**Response**: 200 OK
```json
[
  {
    "id": 1,
    "frequency": "weekly",
    "next_occurrence": "2026-02-18T09:00:00Z"
  }
]
```

### POST /api/v2/recurrence-patterns/recurring-todo
Create a recurring todo with inline pattern.

**Request Body**:
```json
{
  "todo": {
    "title": "Weekly team standup",
    "description": "Discuss progress and blockers",
    "priority": "high",
    "tags": ["work", "meetings"],
    "due_date": "2026-02-18T09:00:00Z",
    "reminder_offsets": [1440, 60]
  },
  "recurrence_pattern": {
    "frequency": "weekly",
    "interval": 1,
    "end_condition": "never",
    "days_of_week": [0, 2, 4]
  }
}
```

**Response**: 201 Created
```json
{
  "todo": {
    "id": 1,
    "title": "Weekly team standup",
    "recurrence_pattern_id": 1
  },
  "recurrence_pattern": {
    "id": 1,
    "frequency": "weekly"
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {}
}
```

### Error Types

- `bad_request` (400): Invalid request data
- `unauthorized` (401): Authentication required
- `forbidden` (403): Access denied
- `not_found` (404): Resource not found
- `conflict` (409): Resource conflict
- `rate_limit_exceeded` (429): Too many requests
- `internal_server_error` (500): Server error

---

## Rate Limiting

- **Default Limit**: 60 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets
  - `Retry-After`: Seconds to wait (when rate limited)

---

## Examples

### Create a Daily Recurring Task

```bash
curl -X POST http://localhost:8000/api/v2/recurrence-patterns/recurring-todo \
  -H "Content-Type: application/json" \
  -d '{
    "todo": {
      "title": "Daily standup",
      "priority": "high",
      "due_date": "2026-02-12T09:00:00Z"
    },
    "recurrence_pattern": {
      "frequency": "daily",
      "interval": 1,
      "end_condition": "never"
    }
  }'
```

### Get High Priority Incomplete Todos

```bash
curl "http://localhost:8000/api/v2/todos?completed=false&priority=high"
```

### Search for Todos

```bash
curl -X POST http://localhost:8000/api/v2/todos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting", "limit": 10}'
```

### Complete a Recurring Todo

```bash
curl -X POST http://localhost:8000/api/v2/todos/1/complete
```

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

Visit http://localhost:8000/redoc for alternative documentation with ReDoc.
