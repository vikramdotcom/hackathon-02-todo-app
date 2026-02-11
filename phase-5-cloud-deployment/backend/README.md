# Phase V Backend - Todo Chatbot API

FastAPI backend with advanced features: recurring tasks, due dates, priorities, tags, reminders, and event-driven architecture.

## Features

### Phase V Enhancements
- **Recurring Tasks**: Daily, weekly, monthly, yearly patterns with flexible end conditions
- **Due Dates & Priorities**: Task scheduling with 4 priority levels (low, medium, high, urgent)
- **Tags & Search**: Categorize and search tasks efficiently
- **Reminders**: Configurable reminder offsets before due dates
- **Event-Driven**: Dapr integration with Kafka/Redpanda for microservices communication
- **Real-time Updates**: WebSocket support for live synchronization

### API v2 Endpoints

#### Todos
- `POST /api/v2/todos` - Create todo
- `GET /api/v2/todos` - List todos with filtering
- `GET /api/v2/todos/{id}` - Get specific todo
- `PATCH /api/v2/todos/{id}` - Update todo
- `POST /api/v2/todos/{id}/complete` - Complete todo (creates next instance if recurring)
- `DELETE /api/v2/todos/{id}` - Delete todo
- `POST /api/v2/todos/search` - Search todos
- `GET /api/v2/todos/overdue/list` - Get overdue todos
- `GET /api/v2/todos/upcoming/list` - Get upcoming todos

#### Recurrence Patterns
- `POST /api/v2/recurrence-patterns` - Create pattern
- `GET /api/v2/recurrence-patterns/{id}` - Get pattern
- `PATCH /api/v2/recurrence-patterns/{id}` - Update pattern
- `DELETE /api/v2/recurrence-patterns/{id}` - Delete pattern
- `GET /api/v2/recurrence-patterns/active/list` - Get active patterns
- `POST /api/v2/recurrence-patterns/recurring-todo` - Create recurring todo with inline pattern

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or use Docker Compose)
- Dapr CLI (optional, for local Dapr development)

### Local Development with Docker Compose

```bash
# Start all services (PostgreSQL, Redpanda, Backend, Dapr)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Access:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redpanda Console: http://localhost:8080

### Local Development without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_todo_service.py

# Run with verbose output
pytest -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v2/
│   │       ├── __init__.py
│   │       ├── schemas.py       # Pydantic models
│   │       ├── todos.py         # Todo endpoints
│   │       └── recurrence.py    # Recurrence endpoints
│   ├── models/
│   │   ├── todo.py              # Todo model
│   │   └── recurrence.py        # RecurrencePattern model
│   ├── services/
│   │   ├── todo_service.py      # Todo business logic
│   │   └── recurrence_service.py # Recurrence logic
│   ├── database.py              # Database config
│   └── main.py                  # FastAPI app
├── migrations/
│   ├── versions/
│   │   └── 005_add_recurrence_fields.py
│   ├── env.py
│   └── alembic.ini
├── tests/
│   ├── conftest.py              # Test fixtures
│   ├── test_todo_model.py
│   ├── test_todo_service.py
│   └── test_recurrence_model.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Redpanda/Kafka brokers
- `DAPR_HTTP_PORT`: Dapr sidecar HTTP port
- `CORS_ORIGINS`: Allowed CORS origins

## Dapr Integration

The backend integrates with Dapr for:
- **Pub/Sub**: Kafka/Redpanda for event streaming
- **State Store**: PostgreSQL for distributed state
- **Service Invocation**: Inter-service communication

### Running with Dapr

```bash
# Initialize Dapr
dapr init

# Run with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
  --components-path ../k8s/dapr-components \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Examples

### Create a Recurring Todo

```bash
curl -X POST http://localhost:8000/api/v2/recurrence-patterns/recurring-todo \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### List Overdue Todos

```bash
curl http://localhost:8000/api/v2/todos/overdue/list
```

### Search Todos

```bash
curl -X POST http://localhost:8000/api/v2/todos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting", "limit": 10}'
```

## Health Checks

- `/health` - Overall health status
- `/ready` - Readiness probe (Kubernetes)
- `/live` - Liveness probe (Kubernetes)

## Production Deployment

See `../k8s/` for Kubernetes manifests and Helm charts.

## License

MIT
