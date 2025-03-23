#!/bin/sh
# Retry database connection
until poetry run alembic upgrade head; do
  echo "Waiting for database to be ready..."
  sleep 2
done

python app/backend_pre_start.py
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000