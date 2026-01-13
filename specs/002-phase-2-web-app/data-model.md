# Phase 1: Data Model

**Feature**: Phase II – Full-Stack Web Application
**Date**: 2026-01-10
**Status**: Complete

## Overview

This document defines the data model for Phase II, maintaining Phase I's canonical Todo schema while adding User entity for multi-user support. All entities are designed for PostgreSQL storage with SQLModel ORM.

## Entities

### User Entity

**Purpose**: Represents a registered user account with authentication credentials and profile information.

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | Integer | Primary Key, Auto-increment | Generated | Unique user identifier |
| email | String(255) | Unique, Not Null, Email format | - | User's email address (used for login) |
| username | String(100) | Unique, Not Null | - | User's display name |
| hashed_password | String(255) | Not Null | - | Bcrypt hashed password (never plain text) |
| created_at | DateTime | Not Null | NOW() | Account creation timestamp (UTC) |
| updated_at | DateTime | Not Null | NOW() | Last profile update timestamp (UTC) |

**Relationships**:
- One User has many Todos (one-to-many)

**Validation Rules**:
- Email must match regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Username must be 3-50 characters, alphanumeric plus underscore/hyphen
- Password (before hashing) must be 8+ characters with at least one uppercase, one lowercase, one number
- Email and username must be unique across all users

**Indexes**:
- Primary index on `id`
- Unique index on `email`
- Unique index on `username`

**State Transitions**:
- Created → Active (on registration)
- Active → Updated (on profile changes)
- No deletion in Phase II (can be added in future)

---

### Todo Entity

**Purpose**: Represents a single task/action item belonging to a user. Maintains Phase I canonical schema with added user_id foreign key.

**Fields**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | Integer | Primary Key, Auto-increment | Generated | Unique todo identifier |
| user_id | Integer | Foreign Key (users.id), Not Null | - | Owner of this todo |
| title | String(10000) | Not Null | - | Todo title/summary |
| description | Text | Nullable | "" | Detailed description |
| completed | Boolean | Not Null | false | Completion status |
| priority | Enum | Not Null | "medium" | Priority level: low, medium, high |
| tags | Array[String] | Not Null | [] | List of tags for categorization |
| due_date | DateTime | Nullable | null | Optional deadline (UTC) |
| recurrence | String(100) | Nullable | null | Recurrence pattern (storage only) |
| created_at | DateTime | Not Null | NOW() | Creation timestamp (UTC) |
| updated_at | DateTime | Not Null | NOW() | Last modification timestamp (UTC) |

**Relationships**:
- Many Todos belong to one User (many-to-one)

**Validation Rules**:
- Title: 1-10,000 characters, required
- Description: 0-10,000 characters, optional
- Priority: Must be one of: "low", "medium", "high"
- Tags: Each tag 1-50 characters, max 20 tags per todo
- Due date: Must be valid ISO 8601 datetime if provided
- Recurrence: String pattern (not validated in Phase II, processed in future phases)

**Indexes**:
- Primary index on `id`
- Index on `user_id` (for efficient user-specific queries)
- Index on `completed` (for filtering)
- Index on `priority` (for filtering)
- Composite index on `(user_id, completed)` (for common query pattern)

**State Transitions**:
- Created → Pending (completed=false)
- Pending → Completed (completed=true)
- Completed → Pending (completed=false, can be toggled back)
- Any state → Updated (on field modifications)
- Any state → Deleted (removed from database)

**Immutable Fields**:
- `id`: Never changes after creation
- `user_id`: Never changes after creation (todos cannot be transferred)
- `created_at`: Never changes after creation

**Mutable Fields**:
- All other fields can be updated
- `updated_at` automatically updates on any modification

---

## Relationships Diagram

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ username        │
│ hashed_password │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│     Todo        │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │◄─── Foreign Key to User.id
│ title           │
│ description     │
│ completed       │
│ priority        │
│ tags            │
│ due_date        │
│ recurrence      │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Data Integrity Rules

### Foreign Key Constraints

**User → Todo Relationship**:
- Every todo must have a valid user_id referencing an existing user
- On user deletion: Cascade delete all user's todos (or prevent deletion if todos exist)
- On todo creation: user_id must reference existing user

### Unique Constraints

**User Table**:
- Email must be unique across all users
- Username must be unique across all users

**Todo Table**:
- No unique constraints (users can have duplicate titles)

### Check Constraints

**Todo Table**:
- Priority must be one of: 'low', 'medium', 'high'
- Title length: 1-10,000 characters
- Description length: 0-10,000 characters

## Default Values

### User Entity
- `created_at`: Current timestamp (UTC)
- `updated_at`: Current timestamp (UTC)

### Todo Entity
- `completed`: false
- `priority`: "medium"
- `tags`: [] (empty array)
- `description`: "" (empty string)
- `due_date`: null
- `recurrence`: null
- `created_at`: Current timestamp (UTC)
- `updated_at`: Current timestamp (UTC)

## Timestamp Management

### Automatic Timestamp Updates

**On Creation**:
- `created_at` set to current UTC timestamp
- `updated_at` set to current UTC timestamp

**On Update**:
- `created_at` remains unchanged
- `updated_at` set to current UTC timestamp

**Implementation**:
- Database triggers or ORM hooks handle automatic updates
- Application code should not manually set these fields

## Data Migration from Phase I

### Mapping Phase I to Phase II

**Phase I (In-Memory)**:
```python
@dataclass
class Todo:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

**Phase II (Database)**:
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=10000)
    description: str = Field(default="")
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Changes**:
- Added `user_id` foreign key field
- Changed from dataclass to SQLModel
- Added database-specific field constraints
- Same field names, types, and defaults preserved

## Query Patterns

### Common Queries

**Get all todos for a user**:
```sql
SELECT * FROM todos WHERE user_id = ? ORDER BY created_at DESC;
```

**Get pending todos for a user**:
```sql
SELECT * FROM todos WHERE user_id = ? AND completed = false ORDER BY priority DESC, due_date ASC;
```

**Get completed todos for a user**:
```sql
SELECT * FROM todos WHERE user_id = ? AND completed = true ORDER BY updated_at DESC;
```

**Filter by priority**:
```sql
SELECT * FROM todos WHERE user_id = ? AND priority = ? ORDER BY created_at DESC;
```

**Filter by tag**:
```sql
SELECT * FROM todos WHERE user_id = ? AND ? = ANY(tags) ORDER BY created_at DESC;
```

**Search by keyword**:
```sql
SELECT * FROM todos WHERE user_id = ? AND (title ILIKE ? OR description ILIKE ?) ORDER BY created_at DESC;
```

### Performance Considerations

**Indexes Required**:
- `user_id` index: Essential for all user-specific queries
- `completed` index: Improves filtering performance
- `(user_id, completed)` composite index: Optimizes most common query pattern

**Pagination**:
- Use LIMIT and OFFSET for large result sets
- Consider cursor-based pagination for better performance with large datasets

## Data Validation Layers

### Layer 1: Database Constraints
- Foreign key constraints
- Unique constraints
- Check constraints
- Not null constraints

### Layer 2: ORM Validation (SQLModel/Pydantic)
- Field type validation
- String length validation
- Enum validation
- Custom validators

### Layer 3: Service Layer Validation
- Business rule validation
- Cross-field validation
- User permission checks
- Data consistency checks

## Security Considerations

### Password Storage
- Never store plain text passwords
- Use bcrypt with work factor 12
- Hash passwords before storing in database
- Use constant-time comparison for verification

### Data Isolation
- All todo queries must filter by user_id
- Never expose todos from other users
- Validate user_id matches authenticated user
- Use database-level foreign key constraints

### Input Sanitization
- Validate all user input before database operations
- Use parameterized queries (SQLModel handles this)
- Escape special characters in search queries
- Validate email format before storage

## Conclusion

The Phase II data model maintains Phase I's canonical Todo schema while adding User entity for multi-user support. All design decisions support the specification requirements, maintain data integrity, and enable future phase evolution.

**Status**: ✅ Data model complete - Ready for contract generation
