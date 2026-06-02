#!/bin/sh
set -e

# Run database migrations, then start the API server.
# PORT is provided by the platform (Render, etc.); fall back to 8000 locally.
echo "==> Running database migrations (alembic upgrade head)..."
alembic upgrade head

echo "==> Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
