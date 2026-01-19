from celery import Celery

from packages.common.config import get_settings

settings = get_settings()

celery_app = Celery(
    "okx_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.autodiscover_tasks(["packages.tasks"]) 
