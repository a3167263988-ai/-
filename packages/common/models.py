from datetime import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text

from packages.common.db import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False)


class TradePlan(Base):
    __tablename__ = "trade_plans"

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(64), nullable=False, unique=True)
    symbol = Column(String(32), nullable=False)
    market_type = Column(String(16), nullable=False)
    ts = Column(DateTime, nullable=False)
    raw_plan = Column(JSON, nullable=False)
    llm_output = Column(JSON, nullable=True)
    schema_valid = Column(Boolean, default=False)


class RiskDecision(Base):
    __tablename__ = "risk_decisions"

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(64), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(16), nullable=False)
    reasons = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)


class RiskState(Base):
    __tablename__ = "risk_state"

    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    paused = Column(Boolean, default=False)
    reason = Column(String(128), nullable=True)


class OrderInstruction(Base):
    __tablename__ = "order_instructions"

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(64), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(32), nullable=False)
    market_type = Column(String(16), nullable=False)
    side = Column(String(8), nullable=False)
    order_type = Column(String(16), nullable=False)
    qty = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    reduce_only = Column(Boolean, default=False)
    payload = Column(JSON, nullable=False)


class ExchangeReceipt(Base):
    __tablename__ = "exchange_receipts"

    id = Column(Integer, primary_key=True)
    order_instruction_id = Column(Integer, nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(16), nullable=False)
    raw = Column(JSON, nullable=False)


class Fill(Base):
    __tablename__ = "fills"

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(64), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(32), nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    slippage = Column(Float, nullable=False)
    raw = Column(JSON, nullable=False)


class TradeOutcome(Base):
    __tablename__ = "trade_outcomes"

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(64), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    pnl = Column(Float, nullable=False)
    exit_reason = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)
