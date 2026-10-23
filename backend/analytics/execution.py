"""Approved deterministic queries over the demo semantic data layer."""

from collections import defaultdict
from decimal import Decimal

from backend.analytics.metrics import (
    METRIC_CATALOG,
    gross_margin_percent,
    gross_profit,
    percentage_change,
    target_achievement_percent,
)
from backend.analytics.seed_data import SYNTHETIC_SALES, SYNTHETIC_TARGETS
from backend.models import Evidence


def revenue_by_month() -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for row in SYNTHETIC_SALES:
        totals[row.month] += row.revenue
    return dict(sorted(totals.items()))


def metric_evidence(workspace_id: str) -> list[Evidence]:
    monthly = revenue_by_month()
    total_revenue = sum(monthly.values(), Decimal())
    total_cogs = sum(row.cogs for row in SYNTHETIC_SALES)
    total_profit = gross_profit(total_revenue, total_cogs)
    january, march = monthly["2026-01"], monthly["2026-03"]
    region_totals: dict[str, Decimal] = defaultdict(Decimal)
    for row in SYNTHETIC_SALES:
        region_totals[row.region] += row.revenue

    # North March target achievement
    north_march_target = next(
        (t.target_revenue for t in SYNTHETIC_TARGETS if t.region == "North" and t.month == "2026-03"),
        Decimal(130000),
    )
    north_march_actual = next(
        (s.revenue for s in SYNTHETIC_SALES if s.region == "North" and s.month == "2026-03"),
        Decimal(103000),
    )
    north_target_achieved = target_achievement_percent(north_march_actual, north_march_target)

    items = [
        Evidence(
            evidence_id="metric:revenue:2026-q1",
            source_type="metric",
            title="Q1 2026 revenue",
            excerpt=f"Synthetic Q1 revenue: {total_revenue:,.2f}.",
            source_ref="semantic:revenue",
            workspace_id=workspace_id,
        ),
        Evidence(
            evidence_id="metric:profit:2026-q1",
            source_type="metric",
            title="Q1 gross profit",
            excerpt=f"Synthetic Q1 gross profit: {total_profit:,.2f}.",
            source_ref="semantic:gross_profit",
            workspace_id=workspace_id,
        ),
        Evidence(
            evidence_id="metric:growth:jan-mar",
            source_type="metric",
            title="January to March revenue change",
            excerpt=f"Revenue changed {percentage_change(march, january)}% from January ({january:,.2f}) to March ({march:,.2f}).",
            source_ref="semantic:revenue_growth_percent",
            workspace_id=workspace_id,
        ),
        Evidence(
            evidence_id="metric:margin:2026-q1",
            source_type="metric",
            title="Q1 gross margin",
            excerpt=f"Gross margin was {gross_margin_percent(total_revenue, total_cogs)}% using the defined formula.",
            source_ref="semantic:gross_margin_percent",
            workspace_id=workspace_id,
        ),
        Evidence(
            evidence_id="metric:target:north:2026-03",
            source_type="metric",
            title="North March target achievement",
            excerpt=f"North region achieved {north_target_achieved}% of its March target ({north_march_actual:,.2f} of {north_march_target:,.2f}).",
            source_ref="semantic:target_achievement_percent",
            workspace_id=workspace_id,
        ),
        *[
            Evidence(
                evidence_id=f"metric:region:{region.lower()}",
                source_type="metric",
                title=f"{region} revenue",
                excerpt=f"Synthetic Q1 {region} revenue: {value:,.2f}.",
                source_ref="semantic:revenue",
                workspace_id=workspace_id,
            )
            for region, value in sorted(region_totals.items())
        ],
    ]
    return items


def metric_definitions() -> dict[str, str]:
    return {key: item.definition for key, item in METRIC_CATALOG.items()}
