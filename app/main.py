from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from prometheus_client import make_asgi_app

from app.api.deps import require_api_token
from packages.audit.service import log_event
from packages.common.config import get_settings
from packages.common.db import SessionLocal
from packages.common.logging import configure_logging
from packages.common.models import RiskState
from packages.execution.engine import ExecutionEngine
from packages.planner.planner import generate_plan
from packages.regime.engine import infer_regime
from packages.risk.engine import RiskContext, evaluate_plan, set_risk_pause
from packages.signals.extractors import SignalExtractor

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.mount("/metrics", make_asgi_app())


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/status", dependencies=[Depends(require_api_token)])
def status() -> dict:
    session = SessionLocal()
    try:
        risk_state = session.query(RiskState).order_by(RiskState.id.desc()).first()
    finally:
        session.close()
    return {
        "risk_state": {
            "paused": risk_state.paused if risk_state else False,
            "reason": risk_state.reason if risk_state else None,
        }
    }


@app.post("/risk/pause", dependencies=[Depends(require_api_token)])
def pause_risk(reason: str | None = None) -> dict:
    set_risk_pause(True, reason=reason)
    return {"paused": True, "reason": reason}


@app.post("/risk/resume", dependencies=[Depends(require_api_token)])
def resume_risk() -> dict:
    set_risk_pause(False, reason=None)
    return {"paused": False}


@app.post("/plans/generate", dependencies=[Depends(require_api_token)])
def generate(symbol: str, market_type: str = "perp") -> dict:
    signals = SignalExtractor().extract()
    regime = infer_regime()
    log_event("signals", {"signals": [s.__dict__ for s in signals], "regime": regime.__dict__})
    return generate_plan(symbol=symbol, market_type=market_type)


@app.post("/plans/execute", dependencies=[Depends(require_api_token)])
def execute(plan: dict) -> dict:
    session = SessionLocal()
    try:
        risk_state = session.query(RiskState).order_by(RiskState.id.desc()).first()
    finally:
        session.close()

    context = RiskContext(
        equity=100000,
        peak_equity=120000,
        daily_loss_pct=0.0,
        consecutive_losses=0,
        open_positions=0,
        positions_per_symbol=0,
        net_exposure_pct=0.0,
        liquidation_buffer_ratio=settings.liquidation_buffer_ratio,
        risk_state="LOCKDOWN" if risk_state and risk_state.paused else "NORMAL",
    )

    decision = evaluate_plan(plan, context)
    if not decision.allowed:
        raise HTTPException(status_code=400, detail={"reasons": decision.reasons})

    engine = ExecutionEngine(live_trading_enabled=settings.live_trading_enabled)
    result = engine.submit_order(plan)
    return {"status": result.status.value, "receipt": result.receipt}


@app.post("/alerts")
def receive_alerts(payload: dict) -> dict:
    log_event("alertmanager", payload)
    return {"received": True}
