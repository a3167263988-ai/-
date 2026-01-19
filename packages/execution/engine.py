from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from packages.audit.service import log_event
from packages.common.db import SessionLocal
from packages.common.models import ExchangeReceipt, Fill, OrderInstruction


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


@dataclass
class ExecutionResult:
    status: OrderStatus
    receipt: dict


class ExecutionEngine:
    def __init__(self, live_trading_enabled: bool) -> None:
        self.live_trading_enabled = live_trading_enabled

    def submit_order(self, plan: dict) -> ExecutionResult:
        instruction = self._build_instruction(plan)
        self._persist_instruction(instruction)
        receipt = self._paper_fill(instruction)
        status = OrderStatus.FILLED if receipt["status"] == "filled" else OrderStatus.ERROR
        return ExecutionResult(status=status, receipt=receipt)

    def _build_instruction(self, plan: dict) -> dict:
        return {
            "plan_id": plan["meta"]["plan_id"],
            "symbol": plan["meta"]["symbol"],
            "market_type": plan["meta"]["market_type"],
            "side": plan["intent"]["side"],
            "order_type": plan["entry"]["type"],
            "qty": plan["sizing"]["notional_usd"],
            "price": plan["entry"]["price_range"][0],
            "reduce_only": plan["execution"]["reduce_only"],
            "payload": plan,
        }

    def _persist_instruction(self, instruction: dict) -> None:
        session = SessionLocal()
        try:
            order = OrderInstruction(
                plan_id=instruction["plan_id"],
                symbol=instruction["symbol"],
                market_type=instruction["market_type"],
                side=instruction["side"],
                order_type=instruction["order_type"],
                qty=instruction["qty"],
                price=instruction["price"],
                reduce_only=instruction["reduce_only"],
                payload=instruction,
            )
            session.add(order)
            session.commit()
        finally:
            session.close()

    def _paper_fill(self, instruction: dict) -> dict:
        receipt = {
            "status": "filled",
            "ts": datetime.now(timezone.utc).isoformat(),
            "instruction": instruction,
            "paper": True,
        }
        session = SessionLocal()
        try:
            order = session.query(OrderInstruction).order_by(OrderInstruction.id.desc()).first()
            if order:
                exchange_receipt = ExchangeReceipt(
                    order_instruction_id=order.id,
                    status=OrderStatus.FILLED.value,
                    raw=receipt,
                )
                session.add(exchange_receipt)
                fill = Fill(
                    plan_id=instruction["plan_id"],
                    symbol=instruction["symbol"],
                    price=instruction.get("price") or 0.0,
                    qty=instruction["qty"],
                    fee=0.0,
                    slippage=0.0,
                    raw=receipt,
                )
                session.add(fill)
                session.commit()
        finally:
            session.close()

        log_event("order_filled", receipt)
        return receipt
