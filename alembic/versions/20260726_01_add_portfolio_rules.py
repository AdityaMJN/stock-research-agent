"""Add flexible portfolio rules and rule-result storage.

Revision ID: 20260726_01
Revises:
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260726_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolio_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rule_type", sa.String(length=100), nullable=False),
        sa.Column("weight", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_portfolio_rules_rule_type", "portfolio_rules", ["rule_type"])
    op.create_table(
        "rule_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("rule_name", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["stock_id"], ["listings.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_rule_results_stock_id", "rule_results", ["stock_id"])
    op.create_index("ix_rule_results_rule_name", "rule_results", ["rule_name"])
    op.create_index("ix_rule_results_created_at", "rule_results", ["created_at"])
    op.bulk_insert(
        sa.table(
            "portfolio_rules",
            sa.column("rule_name", sa.String), sa.column("description", sa.Text),
            sa.column("rule_type", sa.String), sa.column("weight", sa.Numeric), sa.column("enabled", sa.Boolean),
        ),
        [
            {"rule_name": "Momentum", "description": "Scores positive 3- and 6-month price momentum.", "rule_type": "momentum", "weight": 0.25, "enabled": True},
            {"rule_name": "Strong Uptrend", "description": "Checks price, moving-average, and RSI trend alignment.", "rule_type": "strong_uptrend", "weight": 0.20, "enabled": True},
            {"rule_name": "Golden Cross", "description": "Detects an SMA50 crossover above SMA200.", "rule_type": "golden_cross", "weight": 0.10, "enabled": True},
            {"rule_name": "52 Week High", "description": "Rewards prices trading close to their 52-week high.", "rule_type": "fifty_two_week_high", "weight": 0.15, "enabled": True},
            {"rule_name": "RSI", "description": "Rewards relative strength index readings of 60 or higher.", "rule_type": "rsi", "weight": 0.15, "enabled": True},
            {"rule_name": "SMA200", "description": "Rewards prices trading above their 200-day moving average.", "rule_type": "sma200", "weight": 0.15, "enabled": True},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_rule_results_created_at", table_name="rule_results")
    op.drop_index("ix_rule_results_rule_name", table_name="rule_results")
    op.drop_index("ix_rule_results_stock_id", table_name="rule_results")
    op.drop_table("rule_results")
    op.drop_index("ix_portfolio_rules_rule_type", table_name="portfolio_rules")
    op.drop_table("portfolio_rules")
