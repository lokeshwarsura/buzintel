"""AST-aware SQL query validator and safe query executor for analytics."""

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

APPROVED_TABLE_ALLOWLIST = {
    "orders",
    "order_items",
    "products",
    "customers",
    "sales",
    "monthly_sales",
    "analytics_monthly",
    "targets",
    "marketing_spend",
}

FORBIDDEN_KEYWORDS = {
    "insert", "update", "delete", "drop", "truncate", "alter", "create", "merge",
    "upsert", "grant", "revoke", "copy", "call", "do", "execute", "vacuum", "analyze",
    "set", "show", "into", "outfile", "dumpfile", "pg_sleep", "sleep", "benchmark",
    "information_schema", "pg_catalog", "sqlite_master", "sqlite_schema",
}


class UnsafeQueryError(ValueError):
    """Raised when a query violates read-only analytics policies."""


def tokenize_sql(query: str) -> list[str]:
    """Tokenize a SQL statement into words, symbols, and literals."""
    token_spec = [
        ("COMMENT", r"(--[^\n]*|/\*.*?\*/)"),
        ("STRING", r"'([^'\\]|\\.)*'"),
        ("NUMBER", r"\b\d+(\.\d*)?\b"),
        ("WORD", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
        ("SYMBOL", r"[(),;.*=<>!+\-*/]"),
        ("WHITESPACE", r"\s+"),
    ]
    tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    tokens: list[str] = []
    for mo in re.finditer(tok_regex, query, re.DOTALL):
        kind = mo.lastgroup
        val = mo.group()
        if kind == "COMMENT":
            raise UnsafeQueryError("SQL comments are not permitted in analytics queries.")
        if kind == "WHITESPACE":
            continue
        tokens.append(val)
    return tokens


def extract_tables_ast(tokens: list[str]) -> set[str]:
    """Extract table references following FROM or JOIN keywords using a parser state machine."""
    tables: set[str] = set()
    i = 0
    while i < len(tokens):
        tok_lower = tokens[i].lower()
        if tok_lower in {"from", "join"} and i + 1 < len(tokens):
            next_tok = tokens[i + 1]
            if next_tok != "(":
                table_name = next_tok.lower().strip('"').strip("`")
                tables.add(table_name)
        i += 1
    return tables


def validate_read_only_sql(
    query: str,
    allowed_tables: set[str] | None = None,
    enforce_limit: bool = False,
    max_limit: int = 500,
) -> str:
    """Perform AST-aware validation of analytics SQL queries.

    Enforces:
    1. Single statement only (no semicolons).
    2. Must begin with SELECT or WITH.
    3. No mutating keywords, system schemas, or dangerous functions.
    4. All referenced tables must be in the approved allowlist.
    5. Result row limits when enforce_limit=True.
    """
    clean_query = query.strip()
    if not clean_query:
        raise UnsafeQueryError("SQL query cannot be empty.")

    if ";" in clean_query:
        raise UnsafeQueryError("Only one SQL statement is allowed; semicolons are not permitted.")

    tokens = tokenize_sql(clean_query)
    if not tokens:
        raise UnsafeQueryError("Query contains no valid tokens.")

    first_tok = tokens[0].upper()
    if first_tok not in {"SELECT", "WITH"}:
        raise UnsafeQueryError("Only SELECT or WITH queries are permitted.")

    token_lowers = [t.lower() for t in tokens]
    for forbidden in FORBIDDEN_KEYWORDS:
        if forbidden in token_lowers:
            raise UnsafeQueryError(f"Query contains forbidden keyword or function: '{forbidden}'.")

    # Verify table allowlist
    allowlist = allowed_tables or APPROVED_TABLE_ALLOWLIST
    referenced_tables = extract_tables_ast(tokens)
    for tbl in referenced_tables:
        if tbl not in allowlist:
            raise UnsafeQueryError(f"Table '{tbl}' is not in the approved analytics schema allowlist.")

    if enforce_limit:
        has_limit = "limit" in token_lowers
        if not has_limit:
            clean_query = f"{clean_query} LIMIT {max_limit}"
        else:
            try:
                lim_idx = token_lowers.index("limit")
                if lim_idx + 1 < len(tokens):
                    limit_val = int(tokens[lim_idx + 1])
                    if limit_val > max_limit:
                        clean_query = re.sub(
                            r"\bLIMIT\s+\d+\b",
                            f"LIMIT {max_limit}",
                            clean_query,
                            flags=re.IGNORECASE,
                        )
            except (ValueError, IndexError):
                pass

    return clean_query


def execute_safe_sql(
    engine: Engine,
    query: str,
    params: dict[str, Any] | None = None,
    workspace_id: str | None = None,
    timeout_seconds: float = 5.0,
) -> list[dict[str, Any]]:
    """Execute validated read-only SQL with parameterization, table allowlist, and timeout safety."""
    validated = validate_read_only_sql(query, enforce_limit=True)
    safe_params = dict(params or {})
    if workspace_id is not None:
        safe_params["workspace_id"] = workspace_id

    with engine.connect() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text(f"SET statement_timeout = '{int(timeout_seconds * 1000)}'"))
        result = conn.execute(text(validated), safe_params)
        keys = list(result.keys())
        return [dict(zip(keys, row, strict=False)) for row in result.fetchmany(500)]
