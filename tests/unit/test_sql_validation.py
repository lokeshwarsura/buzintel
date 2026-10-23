import pytest
from sqlalchemy import create_engine

from backend.analytics.sql_validation import (
    UnsafeQueryError,
    execute_safe_sql,
    validate_read_only_sql,
)


def test_allows_single_select_statement() -> None:
    assert (
        validate_read_only_sql("SELECT revenue FROM analytics_monthly")
        == "SELECT revenue FROM analytics_monthly"
    )


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM orders",
        "SELECT 1; DROP TABLE orders",
        "UPDATE orders SET total = 0",
        "INSERT INTO orders VALUES (1)",
        "SELECT * FROM secrets",  # unapproved table
        "SELECT pg_sleep(5) FROM orders",  # forbidden function
        "SELECT revenue FROM orders -- secret comment",  # comment rejected
        "SELECT * FROM sqlite_master",  # system table rejected
    ],
)
def test_rejects_mutation_and_multiple_statement_queries(query: str) -> None:
    with pytest.raises(UnsafeQueryError):
        validate_read_only_sql(query)


def test_enforce_limit_appends_or_caps() -> None:
    res = validate_read_only_sql("SELECT revenue FROM orders", enforce_limit=True, max_limit=100)
    assert "LIMIT 100" in res

    res_capped = validate_read_only_sql(
        "SELECT revenue FROM orders LIMIT 5000", enforce_limit=True, max_limit=500
    )
    assert "LIMIT 500" in res_capped


def test_execute_safe_sql_with_mock_engine() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE orders (id INT, total INT)")
        conn.exec_driver_sql("INSERT INTO orders VALUES (1, 100), (2, 250)")

    rows = execute_safe_sql(engine, "SELECT id, total FROM orders")
    assert len(rows) == 2
    assert rows[0]["total"] == 100
