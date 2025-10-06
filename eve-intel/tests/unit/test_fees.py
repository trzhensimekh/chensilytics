"""Tests for fee calculations."""

import pytest

from eve_intel.analytics.fees import (
    calculate_broker_fee,
    calculate_net_margin_pct,
    calculate_net_profit,
    calculate_sales_tax,
    calculate_spread_pct,
    calculate_total_fees,
)


def test_calculate_broker_fee() -> None:
    """Test broker fee calculation."""
    assert calculate_broker_fee(100.0, 3.0) == 3.0
    assert calculate_broker_fee(1000.0, 2.5) == 25.0


def test_calculate_sales_tax() -> None:
    """Test sales tax calculation."""
    assert calculate_sales_tax(100.0, 8.0) == 8.0
    assert calculate_sales_tax(500.0, 5.0) == 25.0


def test_calculate_total_fees() -> None:
    """Test total fees calculation."""
    # Buy at 100, sell at 150
    # Broker fee: 3% on both = 3 + 4.5 = 7.5
    # Sales tax: 8% on sell = 12
    # Total: 19.5
    total = calculate_total_fees(100.0, 150.0, broker_fee_pct=3.0, sales_tax_pct=8.0)
    assert total == pytest.approx(19.5)


def test_calculate_net_profit() -> None:
    """Test net profit calculation."""
    # Buy at 100, sell at 150, qty 10
    # Gross profit: 50 * 10 = 500
    # Fees per unit: 19.5 (from previous test)
    # Total fees: 195
    # Net profit: 305
    profit = calculate_net_profit(100.0, 150.0, 10, broker_fee_pct=3.0, sales_tax_pct=8.0)
    assert profit == pytest.approx(305.0)


def test_calculate_net_margin_pct() -> None:
    """Test net margin percentage calculation."""
    # Net profit for 1 unit = 30.5 (from previous)
    # Margin = (30.5 / 100) * 100 = 30.5%
    margin = calculate_net_margin_pct(100.0, 150.0, broker_fee_pct=3.0, sales_tax_pct=8.0)
    assert margin == pytest.approx(30.5)


def test_calculate_spread_pct() -> None:
    """Test spread percentage calculation."""
    assert calculate_spread_pct(100.0, 150.0) == pytest.approx(50.0)
    assert calculate_spread_pct(200.0, 220.0) == pytest.approx(10.0)


def test_zero_buy_price_edge_case() -> None:
    """Test edge case with zero buy price."""
    assert calculate_net_margin_pct(0.0, 100.0) == 0.0
    assert calculate_spread_pct(0.0, 100.0) == 0.0
