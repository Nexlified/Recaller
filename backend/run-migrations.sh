#!/bin/bash
# Run database migrations
# Usage: ./run-migrations.sh

set -e

echo "Running Alembic database migrations..."

# Check if alembic is available
if ! command -v alembic &> /dev/null; then
    echo "Error: alembic command not found. Make sure you're in the backend directory and have installed dependencies."
    exit 1
fi

# Run migrations
echo "Upgrading database to latest migration..."
alembic upgrade head

echo "Migration completed successfully!"

# Optional: Show current migration status
echo "Current database revision:"
alembic current
