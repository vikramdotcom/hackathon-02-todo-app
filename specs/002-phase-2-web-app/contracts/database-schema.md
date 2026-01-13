# Database Schema

**Feature**: Phase II – Full-Stack Web Application
**Date**: 2026-01-10
**Database**: PostgreSQL 15+ (Neon DB)

## Overview

This document defines the complete database schema for Phase II, including table definitions, indexes, constraints, and relationships. The schema is designed for PostgreSQL and will be managed using Alembic migrations.

## Tables

### users

**Purpose**: Store user account information and authentication credentials

**Table Definition**:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (login credential) |
| username | VARCHAR(100) | UNIQUE, NOT NULL | User's display name |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp (UTC) |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp (UTC) |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

**Constraints**:
```sql
ALTER TABLE users ADD CONSTRAINT chk_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users ADD CONSTRAINT chk_username_length
    CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 50);
```

**Triggers**:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### todos

**Purpose**: Store todo items with full Phase I canonical schema plus user ownership

**Table Definition**:

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(10000) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    tags TEXT[] NOT NULL DEFAULT '{}',
    due_date TIMESTAMP,
    recurrence VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing todo identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | Owner of this todo |
| title | VARCHAR(10000) | NOT NULL | Todo title/summary |
| description | TEXT | NOT NULL, DEFAULT '' | Detailed description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'medium' | Priority level |
| tags | TEXT[] | NOT NULL, DEFAULT '{}' | Array of tags |
| due_date | TIMESTAMP | NULL | Optional deadline (UTC) |
| recurrence | VARCHAR(100) | NULL | Recurrence pattern |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp (UTC) |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp (UTC) |

**Indexes**:
```sql
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_completed ON todos(completed);
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_user_completed ON todos(user_id, completed);
CREATE INDEX idx_todos_due_date ON todos(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_todos_tags ON todos USING GIN(tags);
```

**Constraints**:
```sql
ALTER TABLE todos ADD CONSTRAINT fk_todos_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE todos ADD CONSTRAINT chk_priority
    CHECK (priority IN ('low', 'medium', 'high'));

ALTER TABLE todos ADD CONSTRAINT chk_title_length
    CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 10000);

ALTER TABLE todos ADD CONSTRAINT chk_description_length
    CHECK (LENGTH(description) <= 10000);
```

**Triggers**:
```sql
CREATE TRIGGER update_todos_updated_at BEFORE UPDATE ON todos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Relationships

### users → todos (One-to-Many)

**Relationship**: One user can have many todos

**Foreign Key**: `todos.user_id` → `users.id`

**Cascade Behavior**: ON DELETE CASCADE (deleting a user deletes all their todos)

**Diagram**:
```
users (1) ──────< (N) todos
  id                   user_id (FK)
```

---

## Indexes Strategy

### Primary Indexes

**users.id**: Automatically created with PRIMARY KEY
**todos.id**: Automatically created with PRIMARY KEY

### Unique Indexes

**users.email**: Ensures email uniqueness for authentication
**users.username**: Ensures username uniqueness for display

### Foreign Key Indexes

**todos.user_id**: Critical for user-specific queries (most common query pattern)

### Filter Indexes

**todos.completed**: Improves filtering by completion status
**todos.priority**: Improves filtering by priority level
**todos.user_id, todos.completed**: Composite index for most common query (user's pending/completed todos)

### Partial Indexes

**todos.due_date**: Partial index only on non-null due dates (improves queries for todos with deadlines)

### Array Indexes

**todos.tags**: GIN index for efficient array containment queries (tag filtering)

---

## Data Types

### PostgreSQL-Specific Types

**SERIAL**: Auto-incrementing integer (equivalent to INTEGER with sequence)
**TEXT**: Variable-length string (no length limit)
**TEXT[]**: Array of text values (for tags)
**TIMESTAMP**: Date and time without timezone (stored as UTC)
**BOOLEAN**: True/false values

### Type Mappings (SQLModel → PostgreSQL)

| SQLModel Type | PostgreSQL Type | Notes |
|---------------|-----------------|-------|
| int | INTEGER | 4-byte integer |
| str | VARCHAR(n) or TEXT | Variable-length string |
| bool | BOOLEAN | True/false |
| datetime | TIMESTAMP | UTC timestamps |
| List[str] | TEXT[] | Array of strings |
| Optional[T] | T NULL | Nullable column |

---

## Constraints Summary

### Primary Key Constraints

- `users.id`: Unique identifier for users
- `todos.id`: Unique identifier for todos

### Foreign Key Constraints

- `todos.user_id` → `users.id`: Ensures referential integrity

### Unique Constraints

- `users.email`: Prevents duplicate email addresses
- `users.username`: Prevents duplicate usernames

### Check Constraints

- `users.email`: Valid email format
- `users.username`: Length between 3-50 characters
- `todos.priority`: Must be 'low', 'medium', or 'high'
- `todos.title`: Length between 1-10,000 characters
- `todos.description`: Maximum 10,000 characters

### Not Null Constraints

- All required fields have NOT NULL constraint
- Optional fields (due_date, recurrence) allow NULL

---

## Default Values

### users Table

- `created_at`: NOW() (current timestamp)
- `updated_at`: NOW() (current timestamp)

### todos Table

- `description`: '' (empty string)
- `completed`: FALSE
- `priority`: 'medium'
- `tags`: '{}' (empty array)
- `created_at`: NOW() (current timestamp)
- `updated_at`: NOW() (current timestamp)

---

## Triggers

### update_updated_at_column()

**Purpose**: Automatically update `updated_at` timestamp on row modification

**Applies To**: users, todos tables

**Behavior**: Sets `updated_at` to current timestamp before UPDATE operations

**Implementation**:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## Migration Strategy

### Initial Migration (Version 001)

**Creates**:
- users table with all columns, indexes, constraints
- todos table with all columns, indexes, constraints
- Foreign key relationship
- Triggers for updated_at

**Alembic Migration File**: `001_initial_schema.py`

### Future Migrations

**Version 002+**: Schema changes will be managed through Alembic migrations
- Add new columns
- Modify constraints
- Add new indexes
- Data migrations if needed

---

## Query Performance Considerations

### Optimized Query Patterns

**Get user's todos**:
```sql
SELECT * FROM todos WHERE user_id = ? ORDER BY created_at DESC;
-- Uses: idx_todos_user_id
```

**Get user's pending todos**:
```sql
SELECT * FROM todos WHERE user_id = ? AND completed = false;
-- Uses: idx_todos_user_completed (composite index)
```

**Filter by tag**:
```sql
SELECT * FROM todos WHERE user_id = ? AND 'work' = ANY(tags);
-- Uses: idx_todos_user_id + idx_todos_tags (GIN index)
```

**Search by keyword**:
```sql
SELECT * FROM todos WHERE user_id = ? AND (title ILIKE '%keyword%' OR description ILIKE '%keyword%');
-- Uses: idx_todos_user_id + sequential scan on text fields
-- Consider full-text search index for better performance if needed
```

### Index Maintenance

**Automatic**: PostgreSQL automatically maintains indexes
**Monitoring**: Use `pg_stat_user_indexes` to monitor index usage
**Optimization**: Add indexes based on actual query patterns in production

---

## Data Integrity

### Referential Integrity

**Foreign Keys**: Enforced at database level
**Cascade Deletes**: Deleting a user automatically deletes their todos
**Orphan Prevention**: Cannot create todo without valid user_id

### Data Validation

**Database Level**: Check constraints, foreign keys, unique constraints
**Application Level**: SQLModel/Pydantic validation
**Service Level**: Business rule validation

### Transaction Isolation

**Default Level**: READ COMMITTED
**Concurrent Access**: Multiple users can modify their own todos simultaneously
**Locking**: Row-level locking prevents concurrent modifications to same todo

---

## Backup and Recovery

### Backup Strategy

**Neon DB**: Automatic backups (managed by Neon)
**Frequency**: Continuous backups with point-in-time recovery
**Retention**: 7 days (Neon default)

### Recovery Procedures

**Point-in-Time Recovery**: Restore to any point within retention period
**Table-Level Recovery**: Export/import specific tables if needed
**Data Export**: Use `pg_dump` for manual backups

---

## Security Considerations

### Password Storage

**Never store plain text passwords**
**Hash Algorithm**: bcrypt with work factor 12
**Storage**: Only hashed_password stored in database

### SQL Injection Prevention

**Parameterized Queries**: SQLModel uses parameterized queries exclusively
**Input Validation**: All user input validated before database operations
**Prepared Statements**: PostgreSQL prepared statements prevent injection

### Access Control

**Database User**: Application uses dedicated database user with limited permissions
**Permissions**: SELECT, INSERT, UPDATE, DELETE on users and todos tables only
**No DDL**: Application user cannot modify schema (migrations use separate user)

---

## Monitoring and Maintenance

### Performance Monitoring

**Query Performance**: Monitor slow queries with `pg_stat_statements`
**Index Usage**: Monitor with `pg_stat_user_indexes`
**Table Size**: Monitor with `pg_total_relation_size`

### Maintenance Tasks

**VACUUM**: Automatic (autovacuum enabled)
**ANALYZE**: Automatic (autoanalyze enabled)
**REINDEX**: Rarely needed (only if index corruption suspected)

---

## Conclusion

The database schema maintains Phase I's canonical Todo data model while adding User entity for multi-user support. All design decisions support the specification requirements, ensure data integrity, and enable efficient querying.

**Status**: ✅ Database schema complete
