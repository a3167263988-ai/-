from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from packages.audit.service import log_event
from packages.common.config import get_settings
from packages.common.db import SessionLocal
from packages.common.models import RiskDecision, RiskState
from packages.common.notify import send_telegram


@dataclass
class RiskContext:
    equity: float
    peak_equity: float
    daily_loss_pct: float
    consecutive_losses: int
    open_positions: int
    positions_per_symbol: int
    net_exposure_pct: float
    liquidation_buffer_ratio: float
    risk_state: str


@dataclass
class RiskResult:
    allowed: bool
    status: str
    reasons: list[str]
    metrics: dict


def get_risk_state(session: SessionLocal) -> RiskState:
    state = session.query(RiskState).order_by(RiskState.id.desc()).first()
    if not state:
        state = RiskState(paused=False, reason=None)
        session.add(state)
        session.commit()
    return state


def set_risk_pause(paused: bool, reason: str | None = None) -> None:
    session = SessionLocal()
    try:
        state = RiskState(paused=paused, reason=reason)
        session.add(state)
        session.commit()
    finally:
        session.close()
    log_event("risk_pause", {"paused": paused, "reason": reason})
    if paused:
        send_telegram(f"Risk pause triggered: {reason or 'manual'}")


def compute_notional(
    equity: float,
    risk_budget_pct: float,
    stop_distance_pct: float,
    fee_buffer_pct: float,
    slippage_buffer_pct: float,
    volatility_buffer_mult: float,
) -> float:
    buffer_total = (fee_buffer_pct + slippage_buffer_pct) * volatility_buffer_mult
    denominator = stop_distance_pct + buffer_total
    if denominator <= 0:
        return 0
    return equity * risk_budget_pct / denominator


def evaluate_plan(plan: dict, context: RiskContext) -> RiskResult:
    settings = get_settings()
    reasons: list[str] = []

    stop_loss = plan["risk"].get("stop_loss")
    if stop_loss in (None, 0):
        reasons.append("missing_stop_loss")

    if plan["risk"]["max_loss_pct"] > settings.max_loss_pct:
        reasons.append("max_loss_pct_exceeds")

    if plan["sizing"]["leverage"] > settings.max_leverage:
        reasons.append("max_leverage_exceeds")

    if context.open_positions >= settings.max_open_positions:
        reasons.append("max_open_positions")

    if context.positions_per_symbol >= settings.max_positions_per_symbol:
        reasons.append("max_positions_per_symbol")

    if context.net_exposure_pct > settings.max_net_exposure_pct:
        reasons.append("max_net_exposure_pct")

    if context.daily_loss_pct >= settings.max_daily_loss_pct:
        reasons.append("max_daily_loss")

    if context.consecutive_losses >= settings.max_consecutive_losses:
        reasons.append("max_consecutive_losses")

    drawdown = 0.0
    if context.peak_equity > 0:
        drawdown = (context.peak_equity - context.equity) / context.peak_equity
        if drawdown >= settings.max_drawdown_pct:
            reasons.append("max_drawdown")

    if context.risk_state == "LOCKDOWN":
        reasons.append("lockdown")

    stop_distance_pct = 0.0
    entry_range = plan.get("entry", {}).get("price_range") or [0, 0]
    entry_price = entry_range[0] or entry_range[1] or 0
    if entry_price and stop_loss:
        stop_distance_pct = abs(entry_price - stop_loss) / entry_price
    if stop_distance_pct <= 0:
        reasons.append("missing_stop_distance_pct")

    notional_usd = compute_notional(
        equity=context.equity,
        risk_budget_pct=plan["risk"]["risk_budget_pct"],
        stop_distance_pct=stop_distance_pct,
        fee_buffer_pct=settings.fee_buffer_pct,
        slippage_buffer_pct=settings.slippage_buffer_pct,
        volatility_buffer_mult=settings.volatility_buffer_mult,
    )

    if plan["sizing"]["notional_usd"] > notional_usd:
        reasons.append("notional_exceeds_risk_budget")

    plan_loss_pct = plan["risk"]["risk_budget_pct"]
    if plan_loss_pct > settings.max_loss_pct:
        reasons.append("single_trade_loss_exceeds")

    allowed = len(reasons) == 0
    status = "APPROVED" if allowed else "REJECTED"

    metrics = {
        "equity": context.equity,
        "drawdown": drawdown,
        "notional_limit": notional_usd,
        "risk_budget_pct": plan["risk"]["risk_budget_pct"],
    }

    session = SessionLocal()
    try:
        decision = RiskDecision(
            plan_id=plan["meta"]["plan_id"],
            ts=datetime.now(timezone.utc),
            status=status,
            reasons=reasons,
            metrics=metrics,
        )
        session.add(decision)
        session.commit()
    finally:
        session.close()

    log_event("risk_decision", {"plan_id": plan["meta"]["plan_id"], "status": status})

    return RiskResult(allowed=allowed, status=status, reasons=reasons, metrics=metrics)
