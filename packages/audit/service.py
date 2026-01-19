from datetime import datetime, timezone

from packages.common.db import SessionLocal
from packages.common.models import AuditEvent


def log_event(event_type: str, payload: dict) -> None:
    session = SessionLocal()
    try:
        event = AuditEvent(ts=datetime.now(timezone.utc), event_type=event_type, payload=payload)
        session.add(event)
        session.commit()
    finally:
        session.close()
