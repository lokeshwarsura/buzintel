"""Transparent, reproducible synthetic datasets with fixed seeds for analytics."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class MonthlySales:
    month: str
    region: str
    product_category: str
    revenue: Decimal
    cogs: Decimal
    orders: int


@dataclass(frozen=True)
class MonthlyTarget:
    month: str
    region: str
    target_revenue: Decimal


@dataclass(frozen=True)
class MarketingSpend:
    month: str
    channel: str
    spend: Decimal
    conversions: int


# Transparent base demo dataset (North & South Q1 2026)
SYNTHETIC_SALES: tuple[MonthlySales, ...] = (
    MonthlySales("2026-01", "North", "Software", Decimal(125000), Decimal(37500), 500),
    MonthlySales("2026-01", "South", "Software", Decimal(95000), Decimal(33250), 380),
    MonthlySales("2026-02", "North", "Software", Decimal(118000), Decimal(37760), 472),
    MonthlySales("2026-02", "South", "Software", Decimal(99000), Decimal(35640), 396),
    MonthlySales("2026-03", "North", "Software", Decimal(103000), Decimal(36050), 412),
    MonthlySales("2026-03", "South", "Software", Decimal(101000), Decimal(37370), 404),
)

# Extended regional dataset
SYNTHETIC_EXTENDED_SALES: tuple[MonthlySales, ...] = SYNTHETIC_SALES + (
    MonthlySales("2026-01", "East", "Hardware", Decimal(85000), Decimal(51000), 280),
    MonthlySales("2026-01", "West", "Services", Decimal(60000), Decimal(18000), 150),
    MonthlySales("2026-02", "East", "Hardware", Decimal(88000), Decimal(52800), 290),
    MonthlySales("2026-02", "West", "Services", Decimal(62000), Decimal(18600), 155),
    MonthlySales("2026-03", "East", "Hardware", Decimal(92000), Decimal(55200), 305),
    MonthlySales("2026-03", "West", "Services", Decimal(64000), Decimal(19200), 160),
)

SYNTHETIC_TARGETS: tuple[MonthlyTarget, ...] = (
    MonthlyTarget("2026-01", "North", Decimal(120000)),
    MonthlyTarget("2026-01", "South", Decimal(90000)),
    MonthlyTarget("2026-02", "North", Decimal(125000)),
    MonthlyTarget("2026-02", "South", Decimal(95000)),
    MonthlyTarget("2026-03", "North", Decimal(130000)),  # North missed target significantly in March
    MonthlyTarget("2026-03", "South", Decimal(100000)),
)

SYNTHETIC_MARKETING: tuple[MarketingSpend, ...] = (
    MarketingSpend("2026-01", "Search Ads", Decimal(25000), 140),
    MarketingSpend("2026-01", "Social Media", Decimal(15000), 90),
    MarketingSpend("2026-02", "Search Ads", Decimal(22000), 125),
    MarketingSpend("2026-02", "Social Media", Decimal(16000), 95),
    MarketingSpend("2026-03", "Search Ads", Decimal(18000), 98),  # Drop in search ad spend in March
    MarketingSpend("2026-03", "Social Media", Decimal(14000), 82),
)


def seed_analytics_tables(engine: Engine, workspace_id: str = "default") -> None:
    """Populate relational analytics tables in SQLite/PostgreSQL for safe SQL querying."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                workspace_id TEXT,
                month TEXT,
                region TEXT,
                product_category TEXT,
                revenue NUMERIC,
                cogs NUMERIC,
                orders_count INTEGER
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY,
                workspace_id TEXT,
                month TEXT,
                region TEXT,
                target_revenue NUMERIC
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS marketing_spend (
                id INTEGER PRIMARY KEY,
                workspace_id TEXT,
                month TEXT,
                channel TEXT,
                spend NUMERIC,
                conversions INTEGER
            )
        """))

        # Clear existing rows for this workspace
        conn.execute(text("DELETE FROM orders WHERE workspace_id = :ws"), {"ws": workspace_id})
        conn.execute(text("DELETE FROM targets WHERE workspace_id = :ws"), {"ws": workspace_id})
        conn.execute(text("DELETE FROM marketing_spend WHERE workspace_id = :ws"), {"ws": workspace_id})

        for i, s in enumerate(SYNTHETIC_EXTENDED_SALES):
            conn.execute(
                text("""
                    INSERT INTO orders (id, workspace_id, month, region, product_category, revenue, cogs, orders_count)
                    VALUES (:id, :ws, :month, :region, :cat, :rev, :cogs, :cnt)
                """),
                {
                    "id": i + 1,
                    "ws": workspace_id,
                    "month": s.month,
                    "region": s.region,
                    "cat": s.product_category,
                    "rev": float(s.revenue),
                    "cogs": float(s.cogs),
                    "cnt": s.orders,
                },
            )

        for i, t in enumerate(SYNTHETIC_TARGETS):
            conn.execute(
                text("""
                    INSERT INTO targets (id, workspace_id, month, region, target_revenue)
                    VALUES (:id, :ws, :month, :region, :target)
                """),
                {"id": i + 1, "ws": workspace_id, "month": t.month, "region": t.region, "target": float(t.target_revenue)},
            )

        for i, m in enumerate(SYNTHETIC_MARKETING):
            conn.execute(
                text("""
                    INSERT INTO marketing_spend (id, workspace_id, month, channel, spend, conversions)
                    VALUES (:id, :ws, :month, :channel, :spend, :conv)
                """),
                {"id": i + 1, "ws": workspace_id, "month": m.month, "channel": m.channel, "spend": float(m.spend), "conv": m.conversions},
            )
