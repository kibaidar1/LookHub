# SocialMediaPoster

SocialMediaPoster is a microservice for posting content to social media platforms (Instagram, Telegram) asynchronously using Celery and Redis.

## Features
- Asynchronous posting to Instagram and Telegram
- Task queueing and retry logic via Celery
- Result notification via Redis pub/sub
- Docker-ready for easy deployment

## Requirements
- Python 3.11+
- Redis (as Celery broker and pub/sub)
- Docker (optional, recommended)

## Quick Start (Docker Compose)

Create a `docker-compose.yaml` in your project root:

```yaml
version: '3.8'
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  socialmediaposter:
    build: ./SocialMediaPoster
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
```

Then run:
```bash
docker compose up --build
```

## Usage

Send a Celery task from your main application (e.g., LookHub):

```python
from celery import Celery

celery_app = Celery(
    "social_media_poster",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

look_data = {...}  # dict with LookRead fields, must include 'task_id'
celery_app.send_task(
    "src.tasks.post_to_social_media",
    args=[look_data]
)
```

Listen for results via Redis pub/sub:
```python
import redis
r = redis.Redis(host='redis', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe(f'social_media_results:{look_data["task_id"]}')
for message in pubsub.listen():
    if message['type'] == 'message':
        print("Got result:", message['data'])
        break
```

## Environment Variables
- `REDIS_HOST` — Redis hostname (default: `localhost`)
- `REDIS_PORT` — Redis port (default: `6379`)
- `TELEGRAM_TOKEN`, `TELEGRAM_CHANNEL_ID`, `INSTAGRAM_LOGIN`, `INSTAGRAM_PASSWORD` — credentials for social platforms

## Project Structure
- `src/tasks.py` — Celery tasks and orchestration
- `src/services/instagram.py` — Instagram posting logic
- `src/services/telegram.py` — Telegram posting logic
- `Dockerfile` — for building the service

## License
MIT 