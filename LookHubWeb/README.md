# LookHub

LookHub — это FastAPI-приложение для управления образами и одеждой с административной и пользовательской частью.

## Быстрый старт (Docker Compose)

1. **Клонируйте репозиторий и перейдите в папку проекта:**
   ```sh
   git clone <repo-url>
   cd LookHub
   ```

2. **Создайте файл `.env` в корне проекта:**
   ```env
   POSTGRES_DB=lookhub
   POSTGRES_USER=lookhub_user
   POSTGRES_PASSWORD=lookhub_pass
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Запустите проект:**
   ```sh
   docker-compose up --build
   ```

4. **Приложение будет доступно по адресу:**
   - http://localhost:8000

## Структура проекта
- `app/` — исходный код FastAPI-приложения
- `app/static/images/` — директория для загружаемых изображений
- `migrations/` — миграции Alembic
- `docker-compose.yaml` — запуск приложения и базы данных
- `Dockerfile` — сборка контейнера приложения

## Переменные окружения
Все переменные для базы данных и приложения задаются в файле `.env`:
- `POSTGRES_DB` — имя базы данных
- `POSTGRES_USER` — пользователь БД
- `POSTGRES_PASSWORD` — пароль пользователя
- `DB_HOST` — хост базы данных (для docker-compose: `db`)
- `DB_PORT` — порт базы данных (по умолчанию 5432)

## Миграции
Для применения миграций используйте:
```sh
docker-compose exec web alembic upgrade head
```

---

Если возникнут вопросы — пишите! 