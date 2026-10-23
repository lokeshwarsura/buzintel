"""Canonical deterministic KPI calculations.

LLM and agent layers must call these functions rather than reproduce business math.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


class MetricError(ValueError):
    """Raised when inputs cannot support a meaningful metric."""


def _decimal(value: Decimal | float | str) -> Decimal:
    return Decimal(str(value))


def _rounded(value: Decimal, places: int = 2) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def percentage_change(current: Decimal | float | str, previous: Decimal | float | str) -> Decimal:
    """Return percent change; a zero baseline is undefined and must be reported explicitly."""
    current_value, previous_value = _decimal(current), _decimal(previous)
    if previous_value == 0:
        raise MetricError("Percentage change is undefined when the comparison baseline is zero.")
    return _rounded(((current_value - previous_value) / abs(previous_value)) * 100)


def gross_margin_percent(
    revenue: Decimal | float | str, cost_of_goods_sold: Decimal | float | str
) -> Decimal:
    """Return gross margin as a percent of revenue."""
    revenue_value = _decimal(revenue)
    if revenue_value == 0:
        raise MetricError("Gross margin is undefined when revenue is zero.")
    return _rounded(((revenue_value - _decimal(cost_of_goods_sold)) / revenue_value) * 100)


def average_order_value(revenue: Decimal | float | str, orders: int) -> Decimal:
    """Return revenue per order."""
    if orders <= 0:
        raise MetricError("Average order value is undefined when orders are zero or negative.")
    return _rounded(_decimal(revenue) / Decimal(orders))


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    label: str
    definition: str
    unit: str


METRIC_CATALOG: dict[str, MetricDefinition] = {
    "revenue": MetricDefinition("revenue", "Revenue", "Recognized sales before COGS.", "currency"),
    "gross_margin_percent": MetricDefinition(
        "gross_margin_percent", "Gross margin", "(Revenue - COGS) / Revenue * 100.", "percent"
    ),
    "average_order_value": MetricDefinition(
        "average_order_value", "Average order value", "Revenue / order count.", "currency"
    ),
    "revenue_growth_percent": MetricDefinition(
        "revenue_growth_percent",
        "Revenue growth",
        "(Current - prior) / abs(prior) * 100.",
        "percent",
    ),
}
