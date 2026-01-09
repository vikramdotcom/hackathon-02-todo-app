# Phase II: Full-Stack Web Application

**Status**: 🔜 Planned
**Points**: 150
**Due Date**: Dec 14, 2025
**Technology Stack**: Next.js, FastAPI, SQLModel, Neon DB

## Overview

Phase II transforms the CLI todo application into a full-stack web application with a modern frontend, REST API backend, and database persistence.

## Planned Features

### Frontend (Next.js)
- 🔜 Modern, responsive web UI
- 🔜 Real-time updates
- 🔜 User authentication and authorization
- 🔜 Dashboard with todo statistics
- 🔜 Advanced filtering and search
- 🔜 Drag-and-drop todo organization
- 🔜 Dark mode support

### Backend (FastAPI)
- 🔜 RESTful API endpoints
- 🔜 JWT-based authentication
- 🔜 User management
- 🔜 Todo CRUD operations via API
- 🔜 Advanced querying and filtering
- 🔜 API documentation (Swagger/OpenAPI)
- 🔜 Rate limiting and security

### Database (Neon DB + SQLModel)
- 🔜 PostgreSQL database (Neon DB)
- 🔜 SQLModel ORM for type-safe queries
- 🔜 Database migrations
- 🔜 Multi-user data isolation
- 🔜 Persistent storage
- 🔜 Backup and recovery

## Architecture

```
phase-2-web-app/
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # Next.js 14 app directory
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API client
│   │   └── styles/       # CSS/Tailwind styles
│   └── package.json
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── models/       # SQLModel models
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic
│   │   └── core/         # Config, auth, database
│   └── requirements.txt
└── README.md            # This file
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js 14 | React framework with SSR/SSG |
| UI Library | Tailwind CSS | Utility-first CSS framework |
| Backend | FastAPI | High-performance Python API framework |
| ORM | SQLModel | Type-safe ORM combining SQLAlchemy + Pydantic |
| Database | Neon DB | Serverless PostgreSQL |
| Auth | JWT | JSON Web Tokens for authentication |
| API Docs | Swagger/OpenAPI | Auto-generated API documentation |

## API Endpoints (Planned)

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Todos
- `GET /api/todos` - List all todos (with filtering)
- `POST /api/todos` - Create new todo
- `GET /api/todos/{id}` - Get todo by ID
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo
- `PATCH /api/todos/{id}/complete` - Mark complete
- `PATCH /api/todos/{id}/incomplete` - Mark incomplete

### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users/me/stats` - Get user statistics

## Database Schema (Planned)

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Todos Table
```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(10000) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'medium',
    tags TEXT[],
    due_date TIMESTAMP,
    recurrence VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Development Roadmap

### Phase 2.1: Backend Setup
- [ ] Initialize FastAPI project
- [ ] Setup Neon DB connection
- [ ] Create SQLModel models
- [ ] Implement database migrations
- [ ] Setup authentication (JWT)

### Phase 2.2: API Development
- [ ] Implement user registration/login
- [ ] Create todo CRUD endpoints
- [ ] Add filtering and search
- [ ] Implement authorization
- [ ] Add API documentation

### Phase 2.3: Frontend Setup
- [ ] Initialize Next.js project
- [ ] Setup Tailwind CSS
- [ ] Create layout and navigation
- [ ] Implement authentication flow
- [ ] Create API client

### Phase 2.4: UI Development
- [ ] Build todo list components
- [ ] Create todo form (add/edit)
- [ ] Implement filtering UI
- [ ] Add dashboard with statistics
- [ ] Implement dark mode

### Phase 2.5: Integration & Testing
- [ ] Connect frontend to backend
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Deployment preparation

## Prerequisites

- Node.js 18+ (for Next.js)
- Python 3.13+ (for FastAPI)
- Neon DB account
- Git

## Getting Started (Coming Soon)

```bash
# Backend
cd phase-2-web-app/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd phase-2-web-app/frontend
npm install
npm run dev
```

## Migration from Phase I

The Phase I service layer (`TodoManager`) will be adapted to work with the database:
- In-memory operations → Database queries
- Session tracking → User-specific data
- Same business logic, different storage

## Next Phase

**Phase III: AI-Powered Todo Chatbot**
- OpenAI ChatKit integration
- Agents SDK
- Official MCP SDK
- Natural language todo management

See [../phase-3-ai-chatbot/README.md](../phase-3-ai-chatbot/README.md) for Phase III details.

## Status

🔜 **Not Started** - Waiting for Phase I completion and approval.

---

**Previous Phase**: [Phase I - CLI App](../phase-1-cli-app/README.md)
**Next Phase**: [Phase III - AI Chatbot](../phase-3-ai-chatbot/README.md)
