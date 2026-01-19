from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="okx-autotrade", alias="APP_NAME")
    environment: str = Field(default="dev", alias="ENVIRONMENT")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_token: str = Field(default="change_me", alias="API_TOKEN")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="okx_trade", alias="POSTGRES_DB")
    postgres_user: str = Field(default="okx", alias="POSTGRES_USER")
    postgres_password: str = Field(default="okxpass", alias="POSTGRES_PASSWORD")

    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    celery_broker_url: str = Field(default="redis://redis:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://redis:6379/1", alias="CELERY_RESULT_BACKEND"
    )

    okx_api_key: str | None = Field(default=None, alias="OKX_API_KEY")
    okx_api_secret: str | None = Field(default=None, alias="OKX_API_SECRET")
    okx_api_passphrase: str | None = Field(default=None, alias="OKX_API_PASSPHRASE")
    okx_use_sandbox: bool = Field(default=True, alias="OKX_USE_SANDBOX")
    live_trading_enabled: bool = Field(default=False, alias="LIVE_TRADING_ENABLED")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    risk_budget_pct: float = Field(default=0.01, alias="RISK_BUDGET_PCT")
    max_loss_pct: float = Field(default=0.10, alias="MAX_LOSS_PCT")
    max_drawdown_pct: float = Field(default=0.40, alias="MAX_DRAWDOWN_PCT")
    max_leverage: int = Field(default=100, alias="MAX_LEVERAGE")
    margin_mode: str = Field(default="cross", alias="MARGIN_MODE")
    liquidation_buffer_ratio: float = Field(default=0.2, alias="LIQUIDATION_BUFFER_RATIO")
    max_open_positions: int = Field(default=3, alias="MAX_OPEN_POSITIONS")
    max_positions_per_symbol: int = Field(default=1, alias="MAX_POSITIONS_PER_SYMBOL")
    max_net_exposure_pct: float = Field(default=0.6, alias="MAX_NET_EXPOSURE_PCT")
    max_daily_loss_pct: float = Field(default=0.1, alias="MAX_DAILY_LOSS_PCT")
    max_consecutive_losses: int = Field(default=5, alias="MAX_CONSECUTIVE_LOSSES")
    cooldown_minutes: int = Field(default=60, alias="COOLDOWN_MINUTES")

    fee_buffer_pct: float = Field(default=0.0005, alias="FEE_BUFFER_PCT")
    slippage_buffer_pct: float = Field(default=0.001, alias="SLIPPAGE_BUFFER_PCT")
    volatility_buffer_mult: float = Field(default=2.0, alias="VOLATILITY_BUFFER_MULT")
    orderbook_spread_limit_bps: int = Field(default=50, alias="ORDERBOOK_SPREAD_LIMIT_BPS")
    orderbook_depth_min_usd: int = Field(default=100000, alias="ORDERBOOK_DEPTH_MIN_USD")

    plan_schema_path: str = Field(
        default="/app/packages/common/schemas/trade_plan.schema.json",
        alias="PLAN_SCHEMA_PATH",
    )

    grafana_admin_user: str = Field(default="admin", alias="GRAFANA_ADMIN_USER")
    grafana_admin_password: str = Field(default="admin", alias="GRAFANA_ADMIN_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache

def get_settings() -> Settings:
    return Settings()
