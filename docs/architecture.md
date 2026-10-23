# Architecture

The application is a modular monolith. React calls FastAPI; the API requires a workspace header and delegates to one controlled workflow. The workflow retrieves deterministic metric evidence and workspace-scoped document evidence, then emits a structured report with citations, limitations, and trace ID.

```text
React -> FastAPI -> workflow -> [semantic metrics | document store] -> report + evidence ledger
```

The current document store is an in-memory demo adapter. The production adapter remains PostgreSQL + pgvector + full-text search, protected by workspace filters and a dedicated read-only analytics role.

