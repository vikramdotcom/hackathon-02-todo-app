---
title: Todo App API with AI Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Todo App Phase III - Backend API with AI Chatbot

A FastAPI-based REST API for managing todos with user authentication and AI-powered chatbot assistant.

## Features

- User registration and authentication (JWT)
- CRUD operations for todos
- **AI Chatbot Assistant** - Natural language todo management powered by OpenAI GPT-3.5
- **Streaming Responses** - Real-time SSE (Server-Sent Events) for chat
- **Function Calling** - Automated todo operations based on user intent
- **Session Management** - Persistent conversation history
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
- `POST /api/v1/todos/{id}/complete` - Mark todo as complete (authenticated)
- `POST /api/v1/todos/{id}/incomplete` - Mark todo as incomplete (authenticated)

### Users
- `GET /api/v1/users/me` - Get current user info (authenticated)
- `GET /api/v1/users/me/stats` - Get user statistics (authenticated)

### AI Chat (Phase III)
- `POST /api/v1/chat/message` - Send message to AI chatbot (authenticated, streaming)
- `GET /api/v1/chat/sessions/{session_id}` - Get chat session history (authenticated)
- `DELETE /api/v1/chat/sessions/{session_id}` - Delete chat session (authenticated)

## Configuration

Set the following environment variables in Hugging Face Spaces settings:

### Required Secrets
- `SECRET_KEY` - JWT secret key (generate with: `openssl rand -hex 32`)
- `OPENAI_API_KEY` - OpenAI API key from https://platform.openai.com/api-keys
- `DATABASE_URL` - SQLite database URL (default: `sqlite:///./data/todo_app.db`)

### Optional Configuration
- `ENVIRONMENT` - Set to `production` for production deployment
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 1440)
- `BACKEND_CORS_ORIGINS` - JSON array of allowed origins (e.g., `["https://your-frontend.vercel.app"]`)
- `OPENAI_MODEL` - OpenAI model to use (default: `gpt-3.5-turbo`)
- `OPENAI_MAX_TOKENS` - Max tokens per response (default: 1000)
- `OPENAI_TEMPERATURE` - Response creativity (default: 0.7)
- `CHAT_SESSION_TIMEOUT_MINUTES` - Chat session timeout (default: 30)
- `PHASE2_API_BASE_URL` - Base URL for Phase II API calls (default: same server)

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
