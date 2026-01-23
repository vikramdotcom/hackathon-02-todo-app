# Data Model: AI-Powered Todo Chatbot

**Feature**: 1-ai-chatbot
**Date**: 2026-01-22
**Phase**: 1 - Data Model Design

---

## Overview

This document defines the data entities required for the AI-Powered Todo Chatbot feature. Note that **todo data** remains in Phase II's existing database schema. This model covers only the **chat-specific entities** needed for conversation management.

---

## Design Principles

1. **No Phase II Modifications**: Todo entities (User, Todo) remain unchanged in Phase II database
2. **Session-Based Storage**: Conversation data stored in memory (MVP) or Redis (production)
3. **Stateless API**: Each request is self-contained with session_id for context retrieval
4. **Minimal Persistence**: Only active sessions are stored; expired sessions are purged

---

## Entities

### 1. ConversationSession

**Purpose**: Tracks an ongoing chat interaction for a user

**Storage**: In-memory (Python dict) or Redis

**Lifecycle**: Created on first message, expires after 30 minutes of inactivity

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string (UUID) | Yes | Unique identifier for the conversation session |
| user_id | integer | Yes | Foreign key to Phase II User (from JWT) |
| created_at | datetime | Yes | When the session was created (UTC) |
| last_activity_at | datetime | Yes | Last message timestamp (UTC) |
| message_count | integer | Yes | Total messages in this session |
| context | ConversationContext | Yes | Current conversation context |
| messages | list[ChatMessage] | Yes | Message history (max 20 messages) |

**Validation Rules**:
- session_id must be valid UUID v4
- user_id must match authenticated user
- last_activity_at must be >= created_at
- message_count must be >= 0
- messages list max length: 20 (sliding window)

**State Transitions**:
- `active`: Session is active (last_activity < 30 minutes ago)
- `expired`: Session inactive for > 30 minutes (eligible for cleanup)

**Indexes** (if using Redis):
- Primary key: session_id
- Secondary index: user_id (for user session lookup)
- TTL: 30 minutes from last_activity_at

---

### 2. ChatMessage

**Purpose**: Individual message in a conversation

**Storage**: Embedded in ConversationSession

**Lifecycle**: Created when user sends message or system responds

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_id | string (UUID) | Yes | Unique identifier for this message |
| role | enum | Yes | Message sender: "user" or "assistant" |
| content | string | Yes | Message text content |
| timestamp | datetime | Yes | When message was created (UTC) |
| metadata | MessageMetadata | No | Additional message information |

**Validation Rules**:
- role must be "user" or "assistant"
- content max length: 10,000 characters
- content min length: 1 character (no empty messages)
- timestamp must be in UTC

**Message Types** (via metadata):
- `text`: Regular text message
- `todo_display`: Message containing todo cards
- `confirmation_request`: System asking for confirmation
- `error`: Error message to user

---

### 3. MessageMetadata

**Purpose**: Additional context for a message

**Storage**: Embedded in ChatMessage

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_type | string | No | Type of message (text, todo_display, confirmation_request, error) |
| referenced_todos | list[integer] | No | Todo IDs mentioned in this message |
| function_call | FunctionCall | No | LLM function call that generated this message |
| tokens_used | integer | No | Token count for this message (for monitoring) |

---

### 4. FunctionCall

**Purpose**: Record of LLM function call for debugging and context

**Storage**: Embedded in MessageMetadata

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| function_name | string | Yes | Name of function called (e.g., "create_todo") |
| arguments | dict | Yes | Function arguments as JSON |
| result | dict | No | Function execution result |
| error | string | No | Error message if function failed |

---

### 5. ConversationContext

**Purpose**: Maintains state and references within conversation

**Storage**: Embedded in ConversationSession

**Lifecycle**: Updated with each message exchange

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| referenced_todos | dict[int, TodoReference] | Yes | Recently mentioned todos (for context resolution) |
| last_query_results | list[integer] | No | Todo IDs from last query (for "the first one" references) |
| pending_confirmation | PendingConfirmation | No | Awaiting user confirmation for destructive operation |
| user_preferences | dict | No | User preferences (future: timezone, language) |

**Validation Rules**:
- referenced_todos max size: 50 entries
- last_query_results max size: 100 IDs
- pending_confirmation expires after 2 minutes

---

### 6. TodoReference

**Purpose**: Cached todo information for context resolution

**Storage**: Embedded in ConversationContext

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| todo_id | integer | Yes | Todo ID from Phase II |
| title | string | Yes | Todo title (cached for display) |
| completed | boolean | Yes | Completion status (cached) |
| last_mentioned_at | datetime | Yes | When this todo was last referenced |

**Lifecycle**: Expires after 10 minutes or when conversation context is cleared

---

### 7. PendingConfirmation

**Purpose**: Tracks destructive operations awaiting user confirmation

**Storage**: Embedded in ConversationContext

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| operation | string | Yes | Operation type: "delete", "bulk_delete", "bulk_update" |
| target_todo_ids | list[integer] | Yes | Todo IDs that will be affected |
| created_at | datetime | Yes | When confirmation was requested |
| expires_at | datetime | Yes | When this confirmation expires (created_at + 2 minutes) |
| operation_details | dict | No | Additional operation parameters |

**Validation Rules**:
- operation must be one of: "delete", "bulk_delete", "bulk_update"
- target_todo_ids must not be empty
- expires_at must be > created_at

---

## Entity Relationships

```
ConversationSession (1) ──┬── (N) ChatMessage
                          │
                          └── (1) ConversationContext ──┬── (N) TodoReference
                                                         │
                                                         └── (0..1) PendingConfirmation

ChatMessage (1) ── (0..1) MessageMetadata ── (0..1) FunctionCall
```

---

## Storage Strategy

### MVP (In-Memory)

**Implementation**: Python dictionary
```python
sessions: Dict[str, ConversationSession] = {}
```

**Pros**:
- Simple implementation
- No external dependencies
- Fast access

**Cons**:
- Lost on server restart
- Doesn't scale to multiple instances
- No persistence

**Cleanup Strategy**:
- Background task runs every 5 minutes
- Removes sessions where `last_activity_at < now - 30 minutes`

---

### Production (Redis)

**Implementation**: Redis with JSON serialization

**Key Structure**:
- Session: `chat:session:{session_id}` → JSON
- User index: `chat:user:{user_id}:sessions` → Set of session_ids

**TTL Strategy**:
- Set TTL to 30 minutes on each update
- Redis automatically removes expired sessions

**Pros**:
- Survives server restarts
- Scales to multiple backend instances
- Built-in TTL and cleanup

**Cons**:
- External dependency
- Serialization overhead

---

## Data Flow Examples

### Example 1: New Conversation

```
1. User sends first message (no session_id)
2. Backend creates ConversationSession
   - session_id: generated UUID
   - user_id: from JWT
   - messages: [user_message]
   - context: empty
3. Backend returns session_id to client
4. Client stores session_id in localStorage
```

### Example 2: Multi-Turn Context

```
1. User: "Show me high priority tasks"
2. System queries Phase II API, gets todos [1, 2, 3]
3. System updates context:
   - last_query_results: [1, 2, 3]
   - referenced_todos: {1: {...}, 2: {...}, 3: {...}}
4. User: "Mark the first one complete"
5. System resolves "first one" → todo_id 1 from last_query_results
6. System calls Phase II API to complete todo 1
```

### Example 3: Confirmation Flow

```
1. User: "Delete all completed tasks"
2. System queries Phase II API, finds todos [5, 7, 9]
3. System creates PendingConfirmation:
   - operation: "bulk_delete"
   - target_todo_ids: [5, 7, 9]
   - expires_at: now + 2 minutes
4. System asks: "Delete 3 completed tasks?"
5. User: "Yes"
6. System checks pending_confirmation, executes deletion
7. System clears pending_confirmation
```

---

## Validation & Constraints

### Session Management
- Maximum 20 messages per session (sliding window)
- Session expires after 30 minutes of inactivity
- User can have multiple active sessions (different devices)

### Message Constraints
- User message max length: 10,000 characters
- System response max length: 10,000 characters
- No empty messages allowed

### Context Constraints
- Max 50 referenced todos in context
- Max 100 todo IDs in last_query_results
- Pending confirmations expire after 2 minutes

### Rate Limiting (Future)
- Max 60 messages per user per hour
- Max 10 messages per user per minute

---

## Migration Path

### Phase 3.0 (MVP)
- In-memory session storage
- No persistence
- Single backend instance

### Phase 3.1 (Production)
- Redis session storage
- Multi-instance support
- Optional conversation history persistence

### Phase 3.2 (Enhanced)
- Database tables for conversation history:
  - `conversations` table
  - `messages` table
- User can review past conversations
- Analytics and insights

---

## Notes

- This data model is **independent** of Phase II's database schema
- Todo data remains in Phase II; we only cache references for context
- All timestamps are in UTC
- Session IDs are UUIDs for security (not sequential integers)
- User authentication is handled by Phase II JWT tokens
