# Phase V Backend - Development Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [API Development](#api-development)
- [Database Management](#database-management)
- [Testing Strategy](#testing-strategy)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/vikramdotcom/hackathon-02-todo-app.git
cd hackathon-02-todo-app/phase-5-cloud-deployment/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start Docker services
make docker-up

# Run migrations
make migrate

# Seed database
make seed

# Start development server
make run
```

## Project Architecture

### Directory Structure

```
backend/
├── app/
│   ├── api/v2/          # API endpoints
│   │   ├── todos.py     # Todo endpoints
│   │   └── recurrence.py # Recurrence endpoints
│   ├── models/          # Database models
│   │   ├── todo.py      # Todo model
│   │   └── recurrence.py # RecurrencePattern model
│   ├── services/        # Business logic
│   │   ├── todo_service.py
│   │   └── recurrence_service.py
│   ├── database.py      # Database configuration
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   ├── middleware.py    # Request/response middleware
│   ├── logging_config.py # Logging setup
│   ├── cache.py         # Caching utilities
│   ├── monitoring.py    # Performance monitoring
│   ├── security.py      # Security utilities
│   ├── validators.py    # Input validation
│   ├── pagination.py    # Pagination utilities
│   └── errors.py        # Error handling
├── tests/               # Test suite
├── migrations/          # Alembic migrations
├── scripts/             # Utility scripts
└── Dockerfile           # Docker configuration
```

### Architecture Patterns

**Layered Architecture:**
- **API Layer**: FastAPI endpoints (api/v2/)
- **Service Layer**: Business logic (services/)
- **Data Layer**: Models and database (models/, database.py)

**Dependency Injection:**
- Database sessions injected via FastAPI dependencies
- Configuration injected via get_settings()

**Repository Pattern:**
- Services encapsulate data access logic
- Models define data structure

## Development Workflow

### Daily Development

```bash
# Start development environment
make docker-up

# Run in development mode (auto-reload)
make run

# In another terminal, run tests in watch mode
make test-watch
```

### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint

# Run all quality checks
make format && make lint && make test
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push and create PR
git push origin feature/your-feature
```

## API Development

### Creating New Endpoints

1. **Define Pydantic schemas** in `api/v2/schemas.py`
2. **Implement service methods** in appropriate service file
3. **Create API endpoint** in router file
4. **Add tests** in `tests/`

Example:

```python
# 1. Schema (api/v2/schemas.py)
class TodoCreate(BaseModel):
    title: str
    description: Optional[str]

# 2. Service (services/todo_service.py)
def create_todo(self, title: str, user_id: int) -> Todo:
    todo = Todo(title=title, user_id=user_id)
    self.db.add(todo)
    self.db.commit()
    return todo

# 3. Endpoint (api/v2/todos.py)
@router.post("/")
async def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db)
):
    service = TodoService(db)
    return service.create_todo(data.title, user_id=1)

# 4. Test (tests/test_api_todos.py)
def test_create_todo(client):
    response = client.post("/api/v2/todos/", json={"title": "Test"})
    assert response.status_code == 201
```

### API Documentation

- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Database Management

### Creating Migrations

```bash
# Auto-generate migration
make migrate-create
# Enter migration message when prompted

# Review generated migration
cat migrations/versions/XXX_your_migration.py

# Apply migration
make migrate

# Rollback if needed
make migrate-down
```

### Database Best Practices

- Always use migrations for schema changes
- Add indexes for frequently queried columns
- Use foreign keys for referential integrity
- Add check constraints for data validation
- Test migrations with rollback

## Testing Strategy

### Test Categories

**Unit Tests:**
- Test individual functions and methods
- Mock external dependencies
- Fast execution

**Integration Tests:**
- Test API endpoints
- Use test database
- Test complete workflows

**Example Test Structure:**

```python
class TestTodoService:
    """Test TodoService methods."""

    def test_create_todo(self, session):
        """Test creating a todo."""
        service = TodoService(session)
        todo = service.create_todo("Test", user_id=1)
        assert todo.title == "Test"

    def test_list_todos_with_filter(self, session):
        """Test listing todos with filters."""
        service = TodoService(session)
        todos = service.list_todos(user_id=1, completed=False)
        assert all(not t.completed for t in todos)
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_todo_service.py -v

# Run specific test
pytest tests/test_todo_service.py::TestTodoService::test_create_todo -v

# Run tests matching pattern
pytest -k "test_create" -v
```

## Debugging

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Log with extra fields
logger.info("User action", extra={"user_id": 1, "action": "create_todo"})
```

### Interactive Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### Docker Logs

```bash
# View backend logs
make docker-logs

# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f postgres
```

## Performance Optimization

### Caching

```python
from app.cache import cache_result

@cache_result(ttl=300, key_prefix="user")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

### Database Optimization

- Use indexes for frequently queried columns
- Use select_related/joinedload for relationships
- Implement pagination for large result sets
- Use database connection pooling

### Monitoring

```python
from app.monitoring import PerformanceMonitor

@PerformanceMonitor.time_function
async def slow_operation():
    # Operation code
    pass

# Or use context manager
with PerformanceMonitor.measure_time("database_query"):
    result = db.query(...)
```

## Security Best Practices

### Input Validation

- Always validate user input
- Use Pydantic models for automatic validation
- Sanitize strings to prevent XSS

### Authentication

```python
from app.security import SecurityUtils

# Hash password
hashed = SecurityUtils.hash_password(password)

# Verify password
is_valid = SecurityUtils.verify_password(plain, hashed)

# Create JWT token
token = SecurityUtils.create_access_token({"user_id": 1})
```

### Rate Limiting

```python
from app.rate_limit import check_rate_limit

allowed, remaining = check_rate_limit(user_id)
if not allowed:
    raise HTTPException(status_code=429)
```

### SQL Injection Prevention

- Always use parameterized queries
- Never concatenate user input into SQL
- Use SQLModel/SQLAlchemy ORM

## Common Tasks

### Adding a New Model

1. Create model in `app/models/`
2. Create migration: `make migrate-create`
3. Apply migration: `make migrate`
4. Create service methods
5. Add API endpoints
6. Write tests

### Adding a New API Endpoint

1. Define schemas in `api/v2/schemas.py`
2. Implement service method
3. Create endpoint in router
4. Add tests
5. Update API documentation

### Debugging Database Issues

```bash
# Connect to database
docker-compose exec postgres psql -U todo_user -d todo_db

# View tables
\dt

# View table structure
\d todos

# Run query
SELECT * FROM todos LIMIT 10;
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Database connection error:**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Check database credentials

**Import errors:**
- Ensure virtual environment is activated
- Run `make install` to install dependencies

**Migration conflicts:**
- Check migration history: `alembic history`
- Resolve conflicts manually
- Create new migration if needed

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

## Getting Help

- Check existing issues on GitHub
- Review API documentation at /docs
- Ask in pull request comments
- Contact maintainers
