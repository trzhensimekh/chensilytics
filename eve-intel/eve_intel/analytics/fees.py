"""Trading fees and cost calculations."""

from eve_intel.settings import settings


def calculate_broker_fee(price: float, broker_fee_pct: float | None = None) -> float:
    """Calculate broker fee for a transaction."""
    fee_pct = broker_fee_pct if broker_fee_pct is not None else settings.broker_fee_pct
    return price * (fee_pct / 100.0)


def calculate_sales_tax(price: float, sales_tax_pct: float | None = None) -> float:
    """Calculate sales tax for a transaction."""
    tax_pct = sales_tax_pct if sales_tax_pct is not None else settings.sales_tax_pct
    return price * (tax_pct / 100.0)


def calculate_total_fees(
    buy_price: float,
    sell_price: float,
    broker_fee_pct: float | None = None,
    sales_tax_pct: float | None = None,
) -> float:
    """Calculate total fees for a round-trip trade."""
    # Buy: broker fee
    buy_broker = calculate_broker_fee(buy_price, broker_fee_pct)

    # Sell: broker fee + sales tax
    sell_broker = calculate_broker_fee(sell_price, broker_fee_pct)
    sell_tax = calculate_sales_tax(sell_price, sales_tax_pct)

    return buy_broker + sell_broker + sell_tax


def calculate_net_profit(
    buy_price: float,
    sell_price: float,
    quantity: int = 1,
    broker_fee_pct: float | None = None,
    sales_tax_pct: float | None = None,
) -> float:
    """Calculate net profit after fees."""
    gross_profit = (sell_price - buy_price) * quantity
    total_fees = calculate_total_fees(buy_price, sell_price, broker_fee_pct, sales_tax_pct) * quantity
    return gross_profit - total_fees


def calculate_net_margin_pct(
    buy_price: float,
    sell_price: float,
    broker_fee_pct: float | None = None,
    sales_tax_pct: float | None = None,
) -> float:
    """Calculate net profit margin percentage."""
    net_profit = calculate_net_profit(buy_price, sell_price, 1, broker_fee_pct, sales_tax_pct)
    return (net_profit / buy_price) * 100.0 if buy_price > 0 else 0.0


def calculate_spread_pct(buy_price: float, sell_price: float) -> float:
    """Calculate raw spread percentage."""
    return ((sell_price - buy_price) / buy_price) * 100.0 if buy_price > 0 else 0.0
