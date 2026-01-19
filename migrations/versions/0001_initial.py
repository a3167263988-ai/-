"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
    )
    op.create_table(
        "trade_plans",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("market_type", sa.String(length=16), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("raw_plan", sa.JSON, nullable=False),
        sa.Column("llm_output", sa.JSON, nullable=True),
        sa.Column("schema_valid", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "risk_decisions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reasons", sa.JSON, nullable=False),
        sa.Column("metrics", sa.JSON, nullable=False),
    )
    op.create_table(
        "risk_state",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("paused", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("reason", sa.String(length=128), nullable=True),
    )
    op.create_table(
        "order_instructions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("market_type", sa.String(length=16), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("order_type", sa.String(length=16), nullable=False),
        sa.Column("qty", sa.Float, nullable=False),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column("reduce_only", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("payload", sa.JSON, nullable=False),
    )
    op.create_table(
        "exchange_receipts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_instruction_id", sa.Integer, nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("raw", sa.JSON, nullable=False),
    )
    op.create_table(
        "fills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("qty", sa.Float, nullable=False),
        sa.Column("fee", sa.Float, nullable=False),
        sa.Column("slippage", sa.Float, nullable=False),
        sa.Column("raw", sa.JSON, nullable=False),
    )
    op.create_table(
        "trade_outcomes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("pnl", sa.Float, nullable=False),
        sa.Column("exit_reason", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("trade_outcomes")
    op.drop_table("fills")
    op.drop_table("exchange_receipts")
    op.drop_table("order_instructions")
    op.drop_table("risk_state")
    op.drop_table("risk_decisions")
    op.drop_table("trade_plans")
    op.drop_table("audit_events")
