import json
import logging
from datetime import datetime, timezone
from typing import Any


SENSITIVE_KEYS = {"api_key", "api_secret", "passphrase", "password", "token"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.args:
            payload["args"] = sanitize(record.args)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("***" if key.lower() in SENSITIVE_KEYS else sanitize(val))
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize(item) for item in value]
    return value


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level, handlers=[logging.StreamHandler()])
    root = logging.getLogger()
    for handler in root.handlers:
        handler.setFormatter(JsonFormatter())
