#!/bin/bash
set -e

poetry run alembic upgrade head
poetry run gunicorn app.main:app --workers 2 --timeout 60 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000


