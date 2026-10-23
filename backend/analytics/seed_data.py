"""Small, transparent synthetic data set for the local demo mode."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MonthlySales:
    month: str
    region: str
    product_category: str
    revenue: Decimal
    cogs: Decimal
    orders: int


SYNTHETIC_SALES: tuple[MonthlySales, ...] = (
    MonthlySales("2026-01", "North", "Software", Decimal(125000), Decimal(37500), 500),
    MonthlySales("2026-01", "South", "Software", Decimal(95000), Decimal(33250), 380),
    MonthlySales("2026-02", "North", "Software", Decimal(118000), Decimal(37760), 472),
    MonthlySales("2026-02", "South", "Software", Decimal(99000), Decimal(35640), 396),
    MonthlySales("2026-03", "North", "Software", Decimal(103000), Decimal(36050), 412),
    MonthlySales("2026-03", "South", "Software", Decimal(101000), Decimal(37370), 404),
)
