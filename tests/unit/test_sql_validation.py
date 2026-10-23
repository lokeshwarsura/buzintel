import pytest

from backend.analytics.sql_validation import UnsafeQueryError, validate_read_only_sql


def test_allows_single_select_statement() -> None:
    assert (
        validate_read_only_sql("SELECT revenue FROM analytics_monthly")
        == "SELECT revenue FROM analytics_monthly"
    )


@pytest.mark.parametrize(
    "query", ["DELETE FROM orders", "SELECT 1; DROP TABLE orders", "UPDATE orders SET total = 0"]
)
def test_rejects_mutation_and_multiple_statement_queries(query: str) -> None:
    with pytest.raises(UnsafeQueryError):
        validate_read_only_sql(query)
