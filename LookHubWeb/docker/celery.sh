#!/bin/bash
set -e

poetry run celery -A app.infrastructure.tasks.celery worker -n lookhub-worker --beat --loglevel=info --schedule /tmp/celerybeat-schedule