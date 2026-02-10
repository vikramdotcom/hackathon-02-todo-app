#!/bin/bash
set -e

echo "Starting backend entrypoint script..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h "${DATABASE_HOST:-db}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - continuing..."

# Run database migrations
echo "Running database migrations..."
if [ -d "alembic" ]; then
  alembic upgrade head
  echo "Migrations completed successfully"
else
  echo "No alembic directory found - skipping migrations"
fi

# Execute the main command
echo "Starting application..."
exec "$@"
