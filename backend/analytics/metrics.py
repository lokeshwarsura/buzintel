"""Canonical deterministic KPI calculations.

LLM and agent layers must call these functions rather than reproduce business math.
"""

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


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


def gross_profit(
    revenue: Decimal | float | str, cost_of_goods_sold: Decimal | float | str
) -> Decimal:
    """Return absolute gross profit (Revenue - COGS)."""
    return _rounded(_decimal(revenue) - _decimal(cost_of_goods_sold))


def target_achievement_percent(
    actual: Decimal | float | str, target: Decimal | float | str
) -> Decimal:
    """Return percentage of target achieved (Actual / Target * 100)."""
    target_value = _decimal(target)
    if target_value <= 0:
        raise MetricError("Target achievement is undefined when target is zero or negative.")
    return _rounded((_decimal(actual) / target_value) * 100)


def average_order_value(revenue: Decimal | float | str, orders: int) -> Decimal:
    """Return revenue per order."""
    if orders <= 0:
        raise MetricError("Average order value is undefined when orders are zero or negative.")
    return _rounded(_decimal(revenue) / Decimal(orders))


def detect_time_series_anomalies(
    points: list[tuple[str, Decimal | float | str]],
    threshold_std_dev: float = 1.75,
) -> list[dict[str, Any]]:
    """Detect statistical anomalies in a chronological series using z-scores.

    points: list of (period, value) tuples sorted chronologically.
    Returns list of dicts for points that exceed threshold_std_dev.
    """
    if len(points) < 3:
        return []

    values = [float(_decimal(val)) for _, val in points]
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)

    anomalies = []
    if std_dev == 0:
        return []

    for period, val in points:
        fval = float(_decimal(val))
        z_score = (fval - mean) / std_dev
        if abs(z_score) >= threshold_std_dev:
            anomalies.append({
                "period": period,
                "value": str(val),
                "mean": f"{mean:.2f}",
                "z_score": round(z_score, 2),
                "direction": "spike" if z_score > 0 else "drop",
            })
    return anomalies


def compare_segments(
    current: dict[str, Decimal | float | str],
    prior: dict[str, Decimal | float | str],
) -> list[dict[str, Any]]:
    """Compare performance across segments (regions, products, categories)."""
    comparison = []
    all_keys = sorted(set(current.keys()) | set(prior.keys()))
    for key in all_keys:
        curr_val = _decimal(current.get(key, 0))
        prev_val = _decimal(prior.get(key, 0))
        change = None
        if prev_val != 0:
            change = float(percentage_change(curr_val, prev_val))
        comparison.append({
            "segment": key,
            "current": str(curr_val),
            "prior": str(prev_val),
            "change_percent": change,
        })
    return comparison


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    label: str
    definition: str
    unit: str


METRIC_CATALOG: dict[str, MetricDefinition] = {
    "revenue": MetricDefinition("revenue", "Revenue", "Recognized sales before COGS.", "currency"),
    "gross_profit": MetricDefinition(
        "gross_profit", "Gross profit", "Revenue minus COGS.", "currency"
    ),
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
    "target_achievement_percent": MetricDefinition(
        "target_achievement_percent",
        "Target achievement",
        "Actual revenue / Target revenue * 100.",
        "percent",
    ),
}
