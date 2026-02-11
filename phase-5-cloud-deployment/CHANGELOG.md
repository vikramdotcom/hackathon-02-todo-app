# Phase V Todo Chatbot - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase V cloud-native event-driven architecture
- Recurring tasks with flexible patterns (daily, weekly, monthly, yearly)
- Extended todo model with due dates, priorities, tags, reminders
- API v2 with 17 RESTful endpoints
- Dapr integration for event-driven architecture
- Docker Compose environment for local development
- Comprehensive test suite with 30+ test cases
- Database migrations with Alembic
- Structured logging with JSON formatter
- API middleware for request logging and error handling
- Database seeding script for development
- Makefile for common development tasks
- GitHub Actions CI/CD workflow
- Contributing guidelines

### Changed
- Upgraded to FastAPI with async/await support
- Migrated to SQLModel for better type safety
- Enhanced error handling with global exception handler
- Improved API documentation with OpenAPI/Swagger

### Fixed
- Connection pool exhaustion under high load
- Timezone handling for recurring tasks
- Validation errors for recurrence patterns

## [2.0.0] - 2026-02-11

### Added
- Complete Phase V backend implementation
- RecurrencePattern model with validation
- TodoService with advanced filtering
- RecurrenceService for pattern management
- 11 todo API endpoints
- 6 recurrence pattern API endpoints
- Health check endpoints (/health, /ready, /live)
- Docker configuration with multi-stage build
- PostgreSQL database with connection pooling
- Redpanda (Kafka-compatible) integration
- Test fixtures and utilities
- API integration tests

### Technical Details
- Python 3.11+
- FastAPI 0.104.1
- SQLModel 0.0.14
- Alembic 1.12.1
- Dapr SDK 1.12.0
- PostgreSQL 15
- Redpanda (Kafka-compatible)

## [1.0.0] - 2025-12-15

### Added
- Phase I-IV implementation
- Basic todo CRUD operations
- User authentication
- Chatbot interface
- Local Kubernetes deployment with Minikube
- Helm charts for deployment

### Technical Details
- Python 3.10
- FastAPI
- PostgreSQL
- Kubernetes
- Helm

---

## Release Notes

### Version 2.0.0 - Phase V: Cloud-Native Event-Driven Architecture

This major release transforms the Todo Chatbot into a production-grade, event-driven microservices system with advanced features.

**Key Features:**
- **Recurring Tasks**: Create tasks that repeat automatically (daily, weekly, monthly, yearly)
- **Advanced Scheduling**: Specific days of week, day of month, flexible end conditions
- **Due Dates & Priorities**: Schedule tasks with 4 priority levels
- **Tags & Search**: Categorize and search tasks efficiently
- **Reminders**: Configurable reminder offsets before due dates
- **Event-Driven**: Dapr integration with Kafka/Redpanda for microservices communication

**Breaking Changes:**
- API v2 endpoints use different URL structure (/api/v2/*)
- Database schema extended with new tables (backward compatible)
- Environment variables renamed for consistency

**Migration Guide:**
1. Run database migrations: `alembic upgrade head`
2. Update API client to use v2 endpoints
3. Update environment variables (see .env.example)
4. Test recurring task functionality

**Known Issues:**
- Authentication is stubbed for development (returns user_id=1)
- Dapr integration requires manual setup
- Frontend not yet implemented

**Contributors:**
- Claude Opus 4.6 (AI Assistant)
- Vikram (Project Lead)

---

## Upgrade Guide

### From 1.x to 2.0

1. **Backup your database**
   ```bash
   pg_dump todo_db > backup.sql
   ```

2. **Update dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Update environment variables**
   - Copy .env.example to .env
   - Update DATABASE_URL
   - Add KAFKA_BOOTSTRAP_SERVERS
   - Add DAPR configuration

5. **Test the upgrade**
   ```bash
   make test
   ```

6. **Start the application**
   ```bash
   make docker-up
   ```

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/vikramdotcom/hackathon-02-todo-app/issues
- Documentation: See README.md and CONTRIBUTING.md
