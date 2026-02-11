# Contributing to Phase V Todo Chatbot

Thank you for your interest in contributing to the Phase V Todo Chatbot project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git
- PostgreSQL (or use Docker Compose)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/vikramdotcom/hackathon-02-todo-app.git
cd hackathon-02-todo-app/phase-5-cloud-deployment/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Start Docker services
make docker-up

# Run migrations
make migrate

# Seed database with sample data
make seed

# Run tests
make test
```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**
   ```bash
   make test
   make lint
   make format
   ```

4. **Commit your changes**
   - Follow our commit message guidelines
   - Make small, focused commits

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Code Formatting

We use `black` for code formatting:

```bash
make format
```

### Linting

We use `flake8` and `mypy` for linting:

```bash
make lint
```

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Keep documentation up to date with code changes

Example:
```python
def create_todo(title: str, user_id: int) -> Todo:
    """
    Create a new todo item.

    Args:
        title: The todo title
        user_id: The ID of the user creating the todo

    Returns:
        The created Todo instance

    Raises:
        ValueError: If title is empty
    """
    pass
```

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Aim for high test coverage (>80%)
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Example:
```python
def test_create_todo_with_valid_data(client):
    """Test creating a todo with valid data."""
    # Arrange
    todo_data = {"title": "Test Todo", "description": "Test"}

    # Act
    response = client.post("/api/v2/todos/", json=todo_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test Todo"
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
pytest tests/test_todo_service.py::TestTodoServiceCreate::test_create_basic_todo -v
```

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_model_validation():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_complex_operation():
    pass
```

## Commit Message Guidelines

We follow the Conventional Commits specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes

### Examples

```
feat(api): add endpoint for recurring todos

Add POST /api/v2/recurrence-patterns/recurring-todo endpoint
that creates a todo with an inline recurrence pattern.

Closes #123
```

```
fix(database): resolve connection pool exhaustion

Increase connection pool size and add proper connection cleanup
to prevent pool exhaustion under high load.

Fixes #456
```

## Pull Request Process

1. **Update documentation**
   - Update README.md if needed
   - Add/update API documentation
   - Update CHANGELOG.md

2. **Ensure all checks pass**
   - All tests pass
   - Code is formatted with black
   - No linting errors
   - Coverage is maintained or improved

3. **Create pull request**
   - Use a descriptive title
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

4. **Address review feedback**
   - Respond to comments
   - Make requested changes
   - Push updates to the same branch

5. **Merge**
   - Squash and merge (preferred)
   - Delete branch after merge

## Project Structure

```
backend/
├── app/
│   ├── api/v2/          # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── tests/               # Test suite
├── migrations/          # Alembic migrations
├── scripts/             # Utility scripts
└── Dockerfile           # Docker configuration
```

## Questions?

If you have questions or need help, please:

- Open an issue on GitHub
- Ask in pull request comments
- Contact the maintainers

Thank you for contributing! 🎉
