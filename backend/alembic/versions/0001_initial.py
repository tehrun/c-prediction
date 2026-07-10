"""initial schema
Revision ID: 0001_initial
Revises:
Create Date: 2026-07-09
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_exchanges_key", "exchanges", ["key"], unique=True)
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"], unique=True)
    op.create_table(
        "markets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_id", sa.Integer(), sa.ForeignKey("exchanges.id"), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("exchange_symbol", sa.String(64), nullable=False),
        sa.Column("base_currency", sa.String(32), nullable=False),
        sa.Column("quote_currency", sa.String(32), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("minimum_amount", sa.Numeric(38, 18)),
        sa.Column("minimum_cost", sa.Numeric(38, 18)),
        sa.Column("amount_precision", sa.Integer()),
        sa.Column("price_precision", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("exchange_id", "exchange_symbol"),
    )
    op.create_table(
        "candles",
        sa.Column("exchange_id", sa.Integer(), sa.ForeignKey("exchanges.id"), nullable=False),
        sa.Column("market_id", sa.Integer(), sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("timeframe", sa.String(16), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(38, 18), nullable=False),
        sa.Column("high", sa.Numeric(38, 18), nullable=False),
        sa.Column("low", sa.Numeric(38, 18), nullable=False),
        sa.Column("close", sa.Numeric(38, 18), nullable=False),
        sa.Column("volume", sa.Numeric(38, 18), nullable=False),
        sa.Column("trade_count", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("exchange_id", "market_id", "timeframe", "opened_at"),
    )
    op.create_table(
        "data_quality_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_id", sa.Integer(), sa.ForeignKey("exchanges.id")),
        sa.Column("market_id", sa.Integer(), sa.ForeignKey("markets.id")),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_key", sa.String(32), nullable=False),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
    )
    op.execute("SELECT create_hypertable('candles','opened_at', if_not_exists => TRUE)")
    op.execute(
        "INSERT INTO exchanges (key,name,enabled,created_at,updated_at) "
        "VALUES ('kraken','Kraken',true,now(),now()),"
        "('binance','Binance',true,now(),now()) "
        "ON CONFLICT DO NOTHING"
    )


def downgrade():
    for t in ["ingestion_runs", "data_quality_events", "candles", "markets", "assets", "exchanges"]:
        op.drop_table(t)
