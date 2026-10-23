"""Conservative first-line validation for analytics SQL."""

import re


class UnsafeQueryError(ValueError):
    """Raised when a query is outside the read-only analytics policy."""


_COMMENT_PATTERN = re.compile(r"(--[^\n]*|/\*.*?\*/)", re.DOTALL)
_FORBIDDEN_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|UPSERT|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|COPY|CALL|DO|EXECUTE|VACUUM|ANALYZE|SET|SHOW)\b",
    re.IGNORECASE,
)


def validate_read_only_sql(query: str) -> str:
    """Validate and normalize one analytics statement.

    Actual authorization is enforced separately by the database read-only role.
    """
    normalized = _COMMENT_PATTERN.sub(" ", query).strip()
    if not normalized:
        raise UnsafeQueryError("SQL query cannot be empty.")
    if ";" in normalized:
        raise UnsafeQueryError("Only one SQL statement is allowed; semicolons are not permitted.")
    if not re.match(r"^(SELECT|WITH)\b", normalized, re.IGNORECASE):
        raise UnsafeQueryError("Only SELECT or WITH queries are permitted.")
    if _FORBIDDEN_PATTERN.search(normalized):
        raise UnsafeQueryError("Query contains a forbidden SQL operation.")
    return normalized
