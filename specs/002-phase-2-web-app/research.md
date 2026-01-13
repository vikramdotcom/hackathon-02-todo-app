# Phase 0: Research & Technology Decisions

**Feature**: Phase II – Full-Stack Web Application
**Date**: 2026-01-10
**Status**: Complete

## Overview

This document captures the research findings and technology decisions for Phase II implementation. All decisions are made to support the specification requirements while maintaining Phase I data model semantics and enabling future phase compatibility.

## Technology Stack Decisions

### Frontend Framework: Next.js 14

**Decision**: Use Next.js 14 with React 18 and TypeScript

**Rationale**:
- Server-side rendering (SSR) improves initial page load performance
- App directory structure provides better code organization
- Built-in routing eliminates need for additional router library
- TypeScript provides type safety and better developer experience
- Large ecosystem and community support
- Excellent documentation and learning resources

**Alternatives Considered**:
- **Create React App**: Rejected due to lack of SSR and slower initial loads
- **Vite + React**: Rejected due to need for manual SSR configuration
- **Remix**: Rejected due to smaller ecosystem and less mature tooling

**Best Practices**:
- Use app directory structure (not pages directory)
- Implement client/server component separation
- Use React Server Components for data fetching
- Implement proper error boundaries
- Use Suspense for loading states

### Backend Framework: FastAPI

**Decision**: Use FastAPI 0.104+ with Python 3.13+

**Rationale**:
- Automatic OpenAPI documentation generation (required for Phase III AI agents)
- Native async/await support for better performance
- Pydantic integration for request/response validation
- Type hints throughout for better code quality
- Excellent performance (comparable to Node.js/Go)
- Easy integration with SQLModel for database operations

**Alternatives Considered**:
- **Django REST Framework**: Rejected due to heavier framework overhead and synchronous nature
- **Flask**: Rejected due to lack of built-in async support and validation
- **Node.js/Express**: Rejected to maintain Python consistency with Phase I

**Best Practices**:
- Use dependency injection for database sessions and authentication
- Implement proper exception handling with custom exception handlers
- Use Pydantic models for request/response validation
- Separate business logic into service layer
- Use async database operations throughout

### Database: Neon DB (PostgreSQL)

**Decision**: Use Neon DB (serverless PostgreSQL 15+)

**Rationale**:
- Serverless architecture reduces operational overhead
- Automatic scaling based on usage
- Built-in connection pooling
- PostgreSQL compatibility ensures standard SQL features
- Easy migration to self-hosted PostgreSQL if needed (no vendor lock-in)
- Supports all required features: foreign keys, transactions, indexes

**Alternatives Considered**:
- **SQLite**: Rejected due to lack of concurrent write support
- **MySQL**: Rejected due to less robust JSON support and transaction handling
- **MongoDB**: Rejected due to requirement for relational data model

**Best Practices**:
- Use connection pooling to manage database connections
- Implement proper transaction boundaries
- Use database migrations (Alembic) for schema changes
- Create indexes on foreign keys and frequently queried fields
- Use prepared statements to prevent SQL injection

### ORM: SQLModel

**Decision**: Use SQLModel 0.14+ for database operations

**Rationale**:
- Combines SQLAlchemy and Pydantic for type-safe operations
- Single model definition for database and API schemas
- Excellent type inference and IDE support
- Async support for better performance
- Maintained by FastAPI creator (good integration)

**Alternatives Considered**:
- **SQLAlchemy alone**: Rejected due to need for separate Pydantic models
- **Tortoise ORM**: Rejected due to smaller community and less mature
- **Raw SQL**: Rejected due to lack of type safety and increased boilerplate

**Best Practices**:
- Define models with proper type hints
- Use relationships for foreign keys
- Implement proper cascade delete behavior
- Use SQLModel for both database models and API schemas where possible
- Separate read/write schemas when needed

### Authentication: JWT (JSON Web Tokens)

**Decision**: Use JWT with python-jose for token generation and validation

**Rationale**:
- Stateless authentication (no server-side session storage)
- Scales horizontally without session synchronization
- Standard format supported by all platforms
- Can include user claims in token payload
- Easy to implement with FastAPI

**Alternatives Considered**:
- **Session-based auth**: Rejected due to need for session storage and scaling complexity
- **OAuth2 only**: Rejected as overkill for Phase II (can add in future)
- **API keys**: Rejected due to lack of expiration and user context

**Best Practices**:
- Use short token expiration (24 hours)
- Store tokens in httpOnly cookies (not localStorage)
- Implement token refresh mechanism
- Use strong secret key (256-bit minimum)
- Include minimal claims in token (user_id, email)

### Password Hashing: Passlib with bcrypt

**Decision**: Use passlib with bcrypt algorithm

**Rationale**:
- Industry-standard password hashing
- Configurable work factor for future-proofing
- Resistant to rainbow table attacks
- Well-tested and audited implementation

**Alternatives Considered**:
- **Argon2**: Rejected due to less widespread support (though technically superior)
- **PBKDF2**: Rejected due to lower resistance to GPU attacks
- **Plain SHA**: Rejected due to lack of salt and work factor

**Best Practices**:
- Use bcrypt with work factor of 12 (default)
- Never log or expose password hashes
- Implement password strength requirements
- Use constant-time comparison for password verification

### UI Framework: Tailwind CSS

**Decision**: Use Tailwind CSS 3.x for styling

**Rationale**:
- Utility-first approach reduces CSS bloat
- Excellent responsive design support
- No naming conflicts (no BEM needed)
- Built-in dark mode support
- Excellent Next.js integration

**Alternatives Considered**:
- **CSS Modules**: Rejected due to more boilerplate
- **Styled Components**: Rejected due to runtime overhead
- **Material-UI**: Rejected due to opinionated design and bundle size

**Best Practices**:
- Use Tailwind's responsive modifiers (sm:, md:, lg:)
- Extract common patterns into components
- Use Tailwind's configuration for custom colors/spacing
- Implement dark mode using Tailwind's dark: modifier

## Architecture Patterns

### Layered Architecture (Backend)

**Pattern**: Separate concerns into layers: API → Services → Models → Database

**Rationale**:
- Clear separation of concerns
- Business logic isolated in service layer (reusable for Phase III)
- Easy to test each layer independently
- Follows FastAPI best practices

**Layers**:
1. **API Layer** (routes/): HTTP request/response handling
2. **Service Layer** (services/): Business logic and validation
3. **Model Layer** (models/): Database entities and relationships
4. **Schema Layer** (schemas/): Request/response validation

### Component-Based Architecture (Frontend)

**Pattern**: Organize UI into reusable components with clear responsibilities

**Rationale**:
- Promotes code reuse
- Easier to test and maintain
- Clear component boundaries
- Follows React best practices

**Component Categories**:
1. **Page Components**: Top-level route components
2. **Feature Components**: Domain-specific components (todos, auth)
3. **Layout Components**: Structural components (header, sidebar)
4. **UI Components**: Generic reusable components (button, input)

## Data Flow Patterns

### Frontend → Backend Communication

**Pattern**: REST API with Axios client

**Flow**:
1. User interacts with UI component
2. Component calls API client function
3. Axios sends HTTP request with JWT token
4. Backend validates token and processes request
5. Backend returns JSON response
6. Frontend updates UI based on response

**Error Handling**:
- 401: Redirect to login
- 400: Display validation errors
- 500: Display generic error message
- Network errors: Display retry option

### Database Transaction Boundaries

**Pattern**: One transaction per API request

**Rules**:
- Single todo operations: One transaction
- User registration: One transaction
- Bulk operations: One transaction with rollback on any failure
- Read operations: No transaction needed (autocommit)

## Security Considerations

### Input Validation

**Approach**: Multi-layer validation

**Layers**:
1. **Frontend**: Client-side validation for UX (not security)
2. **API Schema**: Pydantic validation on all requests
3. **Service Layer**: Business rule validation
4. **Database**: Constraints and foreign keys

### SQL Injection Prevention

**Approach**: Use SQLModel/SQLAlchemy parameterized queries exclusively

**Rules**:
- Never concatenate user input into SQL strings
- Use SQLModel query builder for all database operations
- Validate all input types before database operations

### XSS Prevention

**Approach**: React's built-in escaping + Content Security Policy

**Rules**:
- Never use dangerouslySetInnerHTML
- Sanitize any HTML content from users
- Implement CSP headers in production

### CSRF Prevention

**Approach**: SameSite cookies + CORS configuration

**Rules**:
- Set SameSite=Lax on JWT cookies
- Configure CORS to allow only frontend origin
- Use HTTPS in production

## Performance Optimization

### Database Optimization

**Strategies**:
- Index on user_id for todo queries
- Index on email for user lookups
- Use connection pooling (max 20 connections)
- Implement pagination for large result sets

### Frontend Optimization

**Strategies**:
- Use React Server Components for initial render
- Implement code splitting for routes
- Lazy load heavy components
- Use Next.js Image component for optimized images
- Implement proper caching headers

### API Optimization

**Strategies**:
- Use async/await throughout
- Implement response compression (gzip)
- Return only necessary fields in responses
- Use database query optimization (select specific fields)

## Testing Strategy

### Backend Testing

**Approach**: Pytest with fixtures for database and authentication

**Test Types**:
1. **Unit Tests**: Service layer business logic
2. **Integration Tests**: API endpoints with test database
3. **E2E Tests**: Full user flows with test database

**Tools**:
- pytest for test runner
- pytest-asyncio for async tests
- httpx for API testing
- SQLModel with SQLite for test database

### Frontend Testing

**Approach**: Jest + React Testing Library + Playwright

**Test Types**:
1. **Unit Tests**: Component logic and utilities
2. **Integration Tests**: Component interactions
3. **E2E Tests**: Full user flows in browser

**Tools**:
- Jest for unit tests
- React Testing Library for component tests
- Playwright for E2E tests
- MSW (Mock Service Worker) for API mocking

## Development Workflow

### Local Development Setup

**Requirements**:
- Node.js 18+ for frontend
- Python 3.13+ for backend
- Neon DB account (or local PostgreSQL)
- Git for version control

**Setup Steps**:
1. Clone repository
2. Setup backend: Create venv, install dependencies, configure .env
3. Setup frontend: Install npm packages, configure .env.local
4. Run database migrations
5. Start backend dev server (uvicorn with reload)
6. Start frontend dev server (next dev)

### Environment Variables

**Backend (.env)**:
- DATABASE_URL: Neon DB connection string
- SECRET_KEY: JWT signing key (256-bit random)
- ALGORITHM: HS256
- ACCESS_TOKEN_EXPIRE_MINUTES: 1440 (24 hours)

**Frontend (.env.local)**:
- NEXT_PUBLIC_API_URL: Backend API URL (http://localhost:8000)

## Migration from Phase I

### Data Model Mapping

**Phase I → Phase II**:
- In-memory list → PostgreSQL table
- Python dataclass → SQLModel class
- Auto-increment counter → Database sequence
- Session context → User-specific queries (WHERE user_id = ?)

### Business Logic Preservation

**Maintained Semantics**:
- Same validation rules (title required, priority enum, etc.)
- Same default values (priority=medium, completed=false)
- Same field types and constraints
- Same operation semantics (create, update, delete, toggle)

**New Additions**:
- User authentication and authorization
- Multi-user data isolation
- Database persistence
- REST API interface

## Phase III Readiness

### AI Agent Compatibility

**Design Decisions**:
- OpenAPI documentation auto-generated by FastAPI
- Clear, consistent endpoint naming
- Predictable response formats
- Comprehensive error messages
- Stateless API (no session dependencies)

**Future Integration Points**:
- API endpoints can be called by AI agents
- Business logic in service layer can be reused
- Database schema supports additional AI-related fields
- Authentication can be extended for agent access

## Risks and Mitigations

### Risk: Database Connection Limits

**Mitigation**: Use connection pooling with max 20 connections, implement proper connection cleanup

### Risk: JWT Token Theft

**Mitigation**: Use httpOnly cookies, short expiration, HTTPS only in production

### Risk: Performance Degradation with Large Datasets

**Mitigation**: Implement pagination, database indexes, query optimization

### Risk: Breaking Changes Between Phases

**Mitigation**: Maintain Phase I data model semantics, use versioned APIs if needed

## Conclusion

All technology decisions support the Phase II specification requirements while maintaining Phase I compatibility and enabling future phase evolution. The chosen stack (Next.js, FastAPI, SQLModel, Neon DB) provides excellent developer experience, performance, and scalability while avoiding vendor lock-in.

**Status**: ✅ Research complete - Ready for Phase 1 design
