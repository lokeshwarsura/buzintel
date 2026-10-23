"""Approved deterministic queries over the demo semantic data layer."""

from collections import defaultdict
from decimal import Decimal

from backend.analytics.metrics import METRIC_CATALOG, gross_margin_percent, percentage_change
from backend.analytics.seed_data import SYNTHETIC_SALES
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
    january, march = monthly["2026-01"], monthly["2026-03"]
    region_totals: dict[str, Decimal] = defaultdict(Decimal)
    for row in SYNTHETIC_SALES:
        region_totals[row.region] += row.revenue
    return [
        Evidence(
            evidence_id="metric:revenue:2026-q1",
            source_type="metric",
            title="Q1 2026 revenue",
            excerpt=f"Synthetic Q1 revenue: {total_revenue:,.2f}.",
            source_ref="semantic:revenue",
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


def metric_definitions() -> dict[str, str]:
    return {key: item.definition for key, item in METRIC_CATALOG.items()}
