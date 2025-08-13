#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h "$POSTGRES_SERVER" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
