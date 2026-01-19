from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import orjson
from jsonschema import Draft202012Validator

from packages.audit.service import log_event
from packages.common.config import get_settings
from packages.common.models import TradePlan
from packages.common.db import SessionLocal


def load_plan_schema() -> dict:
    settings = get_settings()
    schema_path = Path(settings.plan_schema_path)
    return json.loads(schema_path.read_text())


def build_rule_plan(symbol: str, market_type: str) -> dict:
    plan_id = f"rule-{symbol.lower()}-{uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    return {
        "meta": {
            "symbol": symbol,
            "market_type": market_type,
            "ts": now,
            "timeframe": "1h",
            "plan_id": plan_id,
        },
        "intent": {"side": "flat", "regime": "neutral", "confidence": 0.1},
        "entry": {
            "type": "limit",
            "price_range": [0, 0],
            "conditions": ["no-trade"],
            "tif": "GTC",
        },
        "risk": {
            "stop_loss": 0,
            "take_profit": [],
            "trailing": {"enabled": False, "distance_pct": 0.0},
            "max_loss_pct": 0.0,
            "risk_budget_pct": 0.0,
        },
        "sizing": {
            "leverage": 1,
            "notional_usd": 0,
            "max_position_pct": 0,
            "margin_mode": "cross",
        },
        "execution": {
            "post_only": True,
            "reduce_only": True,
            "max_slippage_bps": 0,
            "timeout_sec": 0,
            "retry_policy": {"max_retries": 0, "backoff_sec": 0},
        },
        "validity": {
            "expires_at": now,
            "invalidation_conditions": ["no-trade"],
        },
        "rationale": {
            "signals_used": ["baseline"],
            "event_summary": "N/A",
            "onchain_summary": "N/A",
            "key_levels": [],
            "notes": "Fallback plan when no valid signal.",
        },
    }


def validate_plan(plan: dict) -> tuple[bool, list[str]]:
    schema = load_plan_schema()
    validator = Draft202012Validator(schema)
    errors = [error.message for error in validator.iter_errors(plan)]
    return (len(errors) == 0, errors)


def generate_plan(symbol: str, market_type: str, llm_output: dict | None = None) -> dict:
    plan = llm_output or build_rule_plan(symbol, market_type)
    is_valid, errors = validate_plan(plan)

    session = SessionLocal()
    try:
        record = TradePlan(
            plan_id=plan["meta"]["plan_id"],
            symbol=plan["meta"]["symbol"],
            market_type=plan["meta"]["market_type"],
            ts=datetime.fromisoformat(plan["meta"]["ts"].replace("Z", "+00:00")),
            raw_plan=plan,
            llm_output=llm_output,
            schema_valid=is_valid,
        )
        session.add(record)
        session.commit()
    finally:
        session.close()

    log_event(
        "plan_generated",
        {"plan": plan, "schema_valid": is_valid, "errors": errors},
    )
    return {"plan": plan, "schema_valid": is_valid, "errors": errors}


def render_plan_json(plan: dict) -> str:
    return orjson.dumps(plan).decode("utf-8")
