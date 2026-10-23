# BizIntel AI REST API Contract

All application routes are versioned under `/api/v1/` unless designated as system health probes.
Authentication uses `Authorization: Bearer <token>` headers. Workspace isolation is enforced via the `X-Workspace-ID: <id>` header.

---

## 1. System Endpoints

### `GET /health`
Liveness probe.
- **Response**: `{"status": "ok", "service": "api"}`

### `GET /ready`
Readiness probe verifying database connectivity.
- **Response**: `{"status": "ready", "database": "connected"}`

---

## 2. Authentication

### `POST /api/v1/auth/register`
- **Request**: `{"email": "user@example.com", "password": "secure-password"}`
- **Response**: `201 Created` — `UserResponse` (`user_id`, `email`, `created_at`)

### `POST /api/v1/auth/login`
- **Request**: `{"email": "user@example.com", "password": "secure-password"}`
- **Response**: `200 OK` — `{"access_token": "...", "token_type": "bearer"}`

### `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `UserResponse`

---

## 3. Workspaces

### `POST /api/v1/workspaces`
- **Headers**: `Authorization: Bearer <token>`
- **Request**: `{"name": "Analytics Workspace"}`
- **Response**: `201 Created` — `WorkspaceResponse` (`workspace_id`, `name`, `role`, `created_at`)

### `GET /api/v1/workspaces`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `list[WorkspaceResponse]`

---

## 4. Datasets & Analytics SQL

### `POST /api/v1/datasets`
- **Headers**: `X-Workspace-ID: <id>`
- **Request**: `{"name": "Sales Ledger", "description": "Q1 2026", "source_type": "csv"}`
- **Response**: `201 Created` — `DatasetResponse`

### `GET /api/v1/datasets`
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `list[DatasetResponse]`

### `POST /api/v1/datasets/{dataset_id}/query`
Executes AST-validated read-only analytics query.
- **Headers**: `X-Workspace-ID: <id>`
- **Request**: `{"query": "SELECT month, region, revenue FROM orders WHERE region = 'North'"}`
- **Response**: `{"rows": [...], "count": 3, "status": "success"}`

---

## 5. Documents & Multi-Format RAG

### `POST /api/v1/documents`
Uploads and indexes documents (PDF, DOCX, TXT, MD, CSV, XLSX).
- **Headers**: `X-Workspace-ID: <id>`
- **Body**: `multipart/form-data` with `file`
- **Response**: `DocumentResponse` (`document_id`, `name`, `content_hash`, `byte_size`, `status`, `created_at`)

### `GET /api/v1/documents`
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `list[DocumentResponse]`

### `GET /api/v1/documents/{document_id}/chunks`
Inspects chunk text, embeddings, and source locations.
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `list[DocumentChunkResponse]`

---

## 6. Conversations & Chat

### `POST /api/v1/conversations`
- **Headers**: `Authorization: Bearer <token>`, `X-Workspace-ID: <id>`
- **Request**: `{"title": "Commercial Audit"}`
- **Response**: `201 Created` — `ConversationResponse`

### `GET /api/v1/conversations`
- **Headers**: `Authorization: Bearer <token>`, `X-Workspace-ID: <id>`
- **Response**: `list[ConversationResponse]`

### `POST /api/v1/conversations/{id}/messages`
Sends user message and triggers agent investigation.
- **Headers**: `X-Workspace-ID: <id>`
- **Request**: `{"content": "Why did North region sales decline in March?"}`
- **Query Param**: `mode=single|multi` (default: `multi`)
- **Response**: `InvestigationReport`

---

## 7. Investigations & Observability

### `POST /api/v1/investigations`
Executes single or hierarchical multi-agent investigation.
- **Headers**: `X-Workspace-ID: <id>`
- **Request**: `{"question": "...", "mode": "multi", "reporting_period": "2026-01 to 2026-03"}`
- **Response**: `InvestigationReport`

### `GET /api/v1/investigations/{id}/timeline`
Returns agent specialist execution steps.
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `list[AgentRunResponse]`

### `GET /api/v1/investigations/{id}/traces`
Returns OpenTelemetry-compatible trace tree.
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `{"trace_id": "...", "root_span": {...}, "spans": [...]}`

---

## 8. Evaluations Laboratory

### `POST /api/v1/evaluations/benchmark`
Executes 10-category benchmark comparing Non-agentic RAG vs Single-Agent vs Multi-Agent.
- **Headers**: `X-Workspace-ID: <id>`
- **Request**: `{"suite_name": "q1_benchmark", "execution_mode": "comparison"}`
- **Response**: `EvaluationRunResponse`

### `GET /api/v1/evaluations/runs`
- **Headers**: `X-Workspace-ID: <id>`
- **Response**: `list[EvaluationRunResponse]`
