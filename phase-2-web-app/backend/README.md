---
title: Todo App API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Todo App Phase II - Backend API

A FastAPI-based REST API for managing todos with user authentication.

## Features

- User registration and authentication (JWT)
- CRUD operations for todos
- SQLite database for data persistence
- OpenAPI documentation at `/docs`
- Health check endpoint at `/health`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get access token

### Todos
- `GET /api/v1/todos` - List all todos (authenticated)
- `POST /api/v1/todos` - Create new todo (authenticated)
- `GET /api/v1/todos/{id}` - Get specific todo (authenticated)
- `PUT /api/v1/todos/{id}` - Update todo (authenticated)
- `DELETE /api/v1/todos/{id}` - Delete todo (authenticated)

### Users
- `GET /api/v1/users/me` - Get current user info (authenticated)

## Configuration

Set the following environment variables in Hugging Face Spaces settings:

### Required Secrets
- `SECRET_KEY` - JWT secret key (generate with: `openssl rand -hex 32`)
- `DATABASE_URL` - SQLite database URL (default: `sqlite:///./data/todo_app.db`)

### Optional Configuration
- `ENVIRONMENT` - Set to `production` for production deployment
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 1440)
- `BACKEND_CORS_ORIGINS` - JSON array of allowed origins (e.g., `["https://your-frontend.hf.space"]`)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Documentation

Once deployed, visit:
- `/docs` - Interactive Swagger UI
- `/redoc` - ReDoc documentation
- `/health` - Health check endpoint

## Tech Stack

- FastAPI - Web framework
- SQLModel - ORM and data validation
- SQLite - Database
- JWT - Authentication
- Alembic - Database migrations
- Pydantic - Data validation
