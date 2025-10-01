import asyncio

import redis
import json
import uuid
import logging
from celery import Celery
from celery.schedules import crontab

from app.application.use_cases import LooksUseCase
from app.config import REDIS_HOST, REDIS_PORT, CELERY_SCHEDULE_HOURS, CELERY_SCHEDULE_MINUTE
from app.domain.entities.looks import LookUpdate
from app.infrastructure.database import async_session_maker
from app.infrastructure.repositories.clothes import ClothesRepository
from app.infrastructure.repositories.looks import LooksRepository

# === ЛОГИРОВАНИЕ ===
logger = logging.getLogger(__name__)

# === Celery config ===
celery_app = Celery(
    "lookhubweb",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def _get_look_use_case():
    looks_repo = LooksRepository(async_session_maker)
    clothes_repo = ClothesRepository(async_session_maker)
    return LooksUseCase(looks_repo, clothes_repo)


@celery_app.task(name='send_looks_to_queue')
def send_looks_to_queue():
    """
    Получаем луки с pushed=False и checked=True
    и отправляем их в очередь SocialMediaPoster.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_send_looks())


async def _send_looks():
    look_use_case = _get_look_use_case()
    looks_to_publish, _ = await look_use_case.get_list(
        page_size=50,
        pushed=False,
        checked=True
    )
    logger.info(f"Found {len(looks_to_publish)} looks ready for publishing")

    for look in looks_to_publish:
        try:
            look_data = look.model_dump()
            task_id = str(uuid.uuid4())
            look_data['task_id'] = task_id

            celery_app.send_task(
                "post_to_social_media",  # имя таски из SocialMediaPoster
                args=[look_data],
                queue="socialmediaposter",  # очередь другого микросервиса
                retry_policy={
                    'max_retries': 3,
                    'interval_start': 10,  # 10 сек
                    'interval_step': 30,
                    'interval_max': 300,  # 5 минут
                }
            )

            logger.info(
                f"Sent look {look.id} ({look.name}) "
                f"to social media queue with task_id={task_id}"
            )
        except Exception as e:
            logger.exception(f"Error sending look {look.id} to social media: {e}")


@celery_app.task(name='process_social_media_results')
def process_social_media_results():
    """
    Обрабатываем результаты от SocialMediaPoster
    и обновляем луки в базе данных.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_process_results())


async def _process_results(batch_size: int = 100):
    look_use_case = _get_look_use_case()
    processed, errors = 0, 0

    for _ in range(batch_size):
        result_json = r.spop("social_media_results_set")
        if not result_json:
            break

        try:
            result = json.loads(result_json)
            logger.info(f"Processing result: {result}")

            if result.get("status") == "success" and result.get("look_id"):
                await look_use_case.update_one(
                    result["look_id"],
                    LookUpdate(pushed=True)
                )
                logger.info(f"Marked look {result['look_id']} as pushed")
                processed += 1
            else:
                logger.warning(f"Invalid result data: {result}")
                errors += 1

        except Exception as e:
            logger.exception(f"Error processing result: {e}")
            errors += 1

    logger.info(f"Processed results: success={processed}, errors={errors}")


celery_app.conf.beat_schedule = {
    'social-then-send': {
        'task': 'process_social_media_results',
        'schedule': crontab(
            hour=CELERY_SCHEDULE_HOURS,
            minute=CELERY_SCHEDULE_MINUTE
        ),
        'options': {'link': send_looks_to_queue.si()},
    }
}