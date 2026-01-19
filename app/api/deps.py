from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from packages.common.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


def require_api_token(api_key: str | None = Security(api_key_header)) -> str:
    settings = get_settings()
    if not api_key or api_key != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return api_key


def get_settings_dep():
    return get_settings()
