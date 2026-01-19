from celery import shared_task

from packages.audit.service import log_event


@shared_task

def health_tick() -> None:
    log_event("heartbeat", {"status": "ok"})
