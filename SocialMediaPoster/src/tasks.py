import logging
import redis
import json
import asyncio
from celery import Celery, group
from celery.exceptions import Ignore

from .entities.looks import LookRead
from .services.instagram import InstagramService
from .services.telegram import TelegramService
from .config import (
    TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID,
    INSTAGRAM_LOGIN, INSTAGRAM_PASSWORD,
    REDIS_HOST, REDIS_PORT
)


logger = logging.getLogger(__name__)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

celery_app = Celery(
    "social_media_poster",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
)


# ---- реестр сервисов ----
SERVICE_REGISTRY = {
    "telegram": lambda: TelegramService(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID),
    "instagram": lambda: InstagramService(INSTAGRAM_LOGIN, INSTAGRAM_PASSWORD),
}


def publish_result(task_id, status, **extra):
    """Запись результата в Redis"""
    r.sadd("social_media_results_set", json.dumps({
        "status": status,
        "task_id": task_id,
        **extra
    }))


def validate_look(look_data, task_id=None) -> LookRead:
    """Преобразуем look_data в модель LookRead"""
    try:
        return LookRead(**look_data)
    except Exception as e:
        logger.error(f"Validation error in LookRead: {e}")
        if task_id:
            publish_result(task_id, "error", error=str(e), look_id=look_data.get("id"))
        raise


def _service_factory(name: str):
    """Возвращает готовый сервис по имени"""
    if name not in SERVICE_REGISTRY:
        raise ValueError(f"Unknown service: {name}")
    return SERVICE_REGISTRY[name]()


# ---- таски ----

@celery_app.task(
    name="post_to_service",
    queue="socialmediaposter",
    bind=True,
    max_retries=3,
    retry_backoff=False,      # без экспоненты
    retry_jitter=False,       # без случайного сдвига
    default_retry_delay=5     # всегда 5 сек
)
def post_to_service(self, service_name: str, look_data: dict):
    """Отправка лука в один конкретный сервис"""
    task_id = look_data.get("task_id")

    try:
        look = validate_look(look_data, task_id)
        service = _service_factory(service_name)

        # ⚡️ Вызов асинхронного метода
        asyncio.run(service.send_new_post(look))

        publish_result(task_id, "success", look_id=look.id, service=service_name)
        logger.info(f"🎉 Posted look {look.id} to {service_name}")

    except Exception as e:
        if self.request.retries < self.max_retries:
            logger.warning(
                f"Retry {self.request.retries + 1}/{self.max_retries} "
                f"for look {look_data.get('id')} in {service_name}: {e}"
            )
            raise self.retry(exc=e)

        publish_result(task_id, "error", look_id=look_data.get("id"),
                       service=service_name, error=str(e))
        logger.error(
            f"❌ Failed to post look {look_data.get('id')} "
            f"to {service_name} after {self.max_retries} retries: {e}"
        )
        raise e


@celery_app.task(name="post_to_social_media")
def post_to_social_media(look_data: dict):
    task_id = look_data.get("task_id")

    # создаём группу subtasks
    job = group(post_to_service.s(service_name, look_data) for service_name in SERVICE_REGISTRY.keys())
    result = job.apply_async()  # можно сохранить result для отслеживания

    logger.info(f"🚀 Dispatched look {look_data.get('id')} ({task_id}) to all services")

