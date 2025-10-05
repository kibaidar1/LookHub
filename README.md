# LookHub

Современное приложение для подбора образов и публикации контента в соцсети. Репозиторий содержит несколько сервисов и инфраструктуру для локальной разработки и продакшн-развертывания на базе Docker.

## Состав проекта

- `LookHubWeb` — основное веб‑приложение (FastAPI), API, админ‑панель, Celery‑задачи
- `SocialMediaPoster` — воркер для публикаций в Telegram/Instagram
- `nginx` — обратный прокси и терминатор SSL
- `postgres` — база данных
- `redis` — брокер сообщений и кэш
- `flower` — мониторинг фоновых задач Celery

Сервисы оркестрируются через `docker-compose.yaml` (dev) и `docker-compose.prod.yaml` (prod).

## Быстрый старт (Dev)

1. Скопируйте примеры переменных окружения:
   - `LookHubWeb/env.example` → `LookHubWeb/.env`
   - `SocialMediaPoster/env.example` → `SocialMediaPoster/.env`

2. Запустите локальную среду:
```bash
docker-compose up -d --build
```

3. Проверка доступности:
```bash
curl -f http://localhost/health
```

Полезные адреса (dev):
- Приложение: `http://localhost/`
- Админ‑панель: `http://localhost/admin/`
- Flower: при необходимости можно раскрыть роут в `nginx.conf`

## Продакшн

1. Создайте `.env.prod` в корне на основе примера (см. раздел «Переменные окружения» ниже и `DEPLOYMENT_PLAN.md`).

2. Соберите и запустите:
```bash
docker-compose -f docker-compose.prod.yaml build --no-cache
docker-compose -f docker-compose.prod.yaml up -d
```

3. Проверка:
```bash
docker-compose -f docker-compose.prod.yaml ps
curl -f http://localhost/health
```

### Nginx и SSL

- Продакшн‑конфиг: `nginx.prod.conf` (маунтится в контейнер `nginx`)
- Порты: 80/443 (HTTPS можно включить, раскомментировав соответствующие директивы)
- Сертификаты ожидаются в `ssl/` (см. скрипт `security/setup-ssl.sh`)

## Переменные окружения

Основные параметры берутся из `.env` файлов сервисов и/или `.env.prod`.

Минимально необходимые (примеры):
```env
# Домен и SSL (prod)
DOMAIN=example.com
SSL_EMAIL=admin@example.com

# БД (PostgreSQL)
POSTGRES_DB=lookhub
POSTGRES_USER=lookhubweb
POSTGRES_PASSWORD=change_me

# Админ‑панель / API
ADMIN_JWT_SECRET=change_me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me
API_KEY=change_me

# Интеграции
INSTAGRAM_LOGIN=login
INSTAGRAM_PASSWORD=pass
TELEGRAM_TOKEN=token
TELEGRAM_CHANNEL_ID=-1001234567890
```

Смотрите также: `LookHubWeb/env.example`, `SocialMediaPoster/env.example`, `DEPLOYMENT_PLAN.md`.

## Директории и артефакты

- `images/` — директория для загружаемых изображений (маппится в `LookHubWeb`)
- `logs/` — логи приложения (маппятся в веб и воркер)
- `nginx-logs/` — логи Nginx
- `postgres-data/` — данные PostgreSQL
- `ssl/` — сертификаты для продакшна
- `monitoring/` — стек мониторинга (Prometheus/Grafana/Loki), см. собственный compose

## Бэкапы и восстановление

В корне есть скрипты для Windows:
- `backup.bat` — создание резервной копии БД/артефактов
- `restore.bat` — восстановление из бэкапа

Бэкапы маунтятся в контейнер Postgres (`./backups:/backups` в prod). Рекомендуется настроить планировщик (Task Scheduler/cron) для автоматизации.

## Мониторинг

Отдельный стек в `monitoring/` (см. `DEPLOYMENT_PLAN.md`):
```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yaml up -d
```
Адреса по умолчанию:
- Grafana: `http://your-domain:3000`
- Prometheus: `http://your-domain:9090`

## Здоровье и логи

- Health‑endpoint: `GET /health` (отдаётся через Nginx)
- Логи сервисов:
```bash
docker-compose logs -f
docker-compose -f docker-compose.prod.yaml logs -f
```

## Частые команды

```bash
# Статус сервисов
docker-compose -f docker-compose.prod.yaml ps

# Пересборка и рестарт
docker-compose -f docker-compose.prod.yaml build --no-cache
docker-compose -f docker-compose.prod.yaml up -d

# Рестарт конкретного сервиса
docker-compose -f docker-compose.prod.yaml restart nginx

# Проверка БД
docker exec -it lookhub-db pg_isready -U lookhubweb -d lookhub
```

## Троблшутинг

- БД не поднимается: проверьте `POSTGRES_*` в `.env.prod`, логи `lookhub-db`
- Веб недоступен: проверьте `lookhub-web` healthcheck, логи Nginx (`nginx-logs/`)
- Очереди/задачи: проверьте Redis health и `lookhub-worker`/`socialmediaposter-worker`
- SSL: проверьте наличие сертификатов в `ssl/` и корректность домена в `nginx.prod.conf`

## Полезные файлы

- `docker-compose.yaml` — локальная разработка
- `docker-compose.prod.yaml` — продакшн
- `nginx.conf`, `nginx.prod.conf` — конфигурация прокси
- `DEPLOYMENT_PLAN.md` — детальный пошаговый план деплоя
- `security/` — утилиты усиления безопасности и настройки SSL

---

Последнее обновление: 2025‑10‑01


