from decimal import Decimal

import pytest

from backend.analytics.metrics import (
    MetricError,
    average_order_value,
    gross_margin_percent,
    percentage_change,
)


def test_percentage_change_uses_prior_period_as_baseline() -> None:
    assert percentage_change("85", "100") == Decimal("-15.00")


def test_percentage_change_rejects_zero_baseline() -> None:
    with pytest.raises(MetricError, match="baseline"):
        percentage_change(10, 0)


def test_gross_margin_percent() -> None:
    assert gross_margin_percent(200, 120) == Decimal("40.00")


def test_average_order_value_rejects_no_orders() -> None:
    with pytest.raises(MetricError, match="orders"):
        average_order_value(100, 0)
