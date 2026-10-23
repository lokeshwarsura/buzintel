# API contract

- `GET /health`: process liveness.
- `GET /ready`: dependency readiness (reports local demo status today).
- `GET /api/v1/metrics/definitions`: canonical KPI definitions.
- `POST /api/v1/investigations`: runs a bounded evidence-driven workflow. Requires `X-Workspace-ID`.
- `POST /api/v1/documents`: uploads TXT/CSV local-demo documents. Requires `X-Workspace-ID`.
- `GET /api/v1/documents`: lists authorized local-demo documents. Requires `X-Workspace-ID`.

Errors use HTTP 401 for missing workspace context and 422 for invalid document input.
