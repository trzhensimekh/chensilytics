"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Items table
    op.create_table(
        'items',
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('volume_m3', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index('ix_items_name', 'items', ['name'])

    # Markets table
    op.create_table(
        'markets',
        sa.Column('hub_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('region_id', sa.BigInteger(), nullable=True),
        sa.Column('system_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('hub_id')
    )

    # Orders snapshot table
    op.create_table(
        'orders_snapshot',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('hub_id', sa.BigInteger(), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('ts_snapshot', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_snapshot_order_id', 'orders_snapshot', ['order_id'])
    op.create_index('ix_orders_snapshot_item_id', 'orders_snapshot', ['item_id'])
    op.create_index('ix_orders_snapshot_hub_id', 'orders_snapshot', ['hub_id'])
    op.create_index('ix_orders_snapshot_ts_snapshot', 'orders_snapshot', ['ts_snapshot'])
    op.create_index('idx_orders_item_hub_ts', 'orders_snapshot', ['item_id', 'hub_id', 'ts_snapshot'])
    op.create_index('idx_orders_hub_ts', 'orders_snapshot', ['hub_id', 'ts_snapshot'])

    # Prices history table
    op.create_table(
        'prices_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('hub_id', sa.BigInteger(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('avg_price', sa.Float(), nullable=True),
        sa.Column('min_price', sa.Float(), nullable=True),
        sa.Column('max_price', sa.Float(), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_prices_history_item_id', 'prices_history', ['item_id'])
    op.create_index('ix_prices_history_hub_id', 'prices_history', ['hub_id'])
    op.create_index('ix_prices_history_date', 'prices_history', ['date'])
    op.create_index('idx_price_hist_item_hub_date', 'prices_history', ['item_id', 'hub_id', 'date'], unique=True)

    # Analytics arbitrage run table
    op.create_table(
        'analytics_arbitrage_run',
        sa.Column('run_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('num_candidates', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('run_id')
    )
    op.create_index('ix_analytics_arbitrage_run_created_at', 'analytics_arbitrage_run', ['created_at'])

    # Analytics arbitrage item table
    op.create_table(
        'analytics_arbitrage_item',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.BigInteger(), nullable=False),
        sa.Column('from_hub_id', sa.BigInteger(), nullable=False),
        sa.Column('to_hub_id', sa.BigInteger(), nullable=False),
        sa.Column('buy_price', sa.Float(), nullable=False),
        sa.Column('sell_price', sa.Float(), nullable=False),
        sa.Column('spread_pct', sa.Float(), nullable=False),
        sa.Column('fees_total', sa.Float(), nullable=False),
        sa.Column('liquidity_24h', sa.Float(), nullable=True),
        sa.Column('ev_isk', sa.Float(), nullable=False),
        sa.Column('net_margin_pct', sa.Float(), nullable=False),
        sa.Column('decay_score', sa.Float(), nullable=True),
        sa.Column('capital_required', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_arbitrage_item_run_id', 'analytics_arbitrage_item', ['run_id'])
    op.create_index('idx_arb_item_run', 'analytics_arbitrage_item', ['run_id', 'item_id'])


def downgrade() -> None:
    op.drop_table('analytics_arbitrage_item')
    op.drop_table('analytics_arbitrage_run')
    op.drop_table('prices_history')
    op.drop_table('orders_snapshot')
    op.drop_table('markets')
    op.drop_table('items')
