.PHONY: help install test lint format clean run docker-up docker-down migrate seed

help:
	@echo "Phase V Backend - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install dependencies"
	@echo "  make run          Run development server"
	@echo "  make seed         Seed database with sample data"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run test suite"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make test-watch   Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         Run linters (flake8, mypy)"
	@echo "  make format       Format code with black"
	@echo "  make format-check Check code formatting"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      Run database migrations"
	@echo "  make migrate-create Create new migration"
	@echo "  make migrate-down Rollback last migration"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    Start Docker services"
	@echo "  make docker-down  Stop Docker services"
	@echo "  make docker-logs  View Docker logs"
	@echo "  make docker-build Build Docker image"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove cache and temp files"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	python scripts/seed_database.py

test:
	pytest -v

test-cov:
	pytest -v --cov=app --cov-report=html --cov-report=term

test-watch:
	pytest-watch -v

lint:
	flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/

format-check:
	black --check app/ tests/

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

docker-build:
	docker build -t todo-backend:latest .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
