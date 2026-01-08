from celery import Celery
from src.core.config import settings


# Инициализация Celery
celery_app = Celery(
    "mailing_service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Настройки для корректной работы в Docker
celery_app.conf.update(
    task_track_started=True, # Выводит информацию о запущенных задачах в консоль
    trust_period=0,          # Не требует подтверждения выполнения задач
)

# Автоматический поиск задач в папке tasks
celery_app.autodiscover_tasks(["src.tasks"])


