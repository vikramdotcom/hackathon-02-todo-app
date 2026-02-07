#!/bin/bash
set -e

echo "Starting backend entrypoint script..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h "${DATABASE_HOST:-database}" -p "${DATABASE_PORT:-5432}" -U "${POSTGRES_USER:-postgres}"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Migrations complete!"

# Execute the main command
echo "Starting application..."
exec "$@"
