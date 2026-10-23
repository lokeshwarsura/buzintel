"""Comprehensive end-to-end integration tests for all BizIntel AI API endpoints."""

import io
from uuid import uuid4

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def get_authenticated_session() -> tuple[dict[str, str], str]:
    email = f"user-{uuid4()}@example.test"
    password = "a-very-secure-password-1234"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg.status_code == 201

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    ws = client.post("/api/v1/workspaces", json={"name": "HQ Analytics"}, headers=headers)
    assert ws.status_code == 201
    ws_id = ws.json()["workspace_id"]
    headers["X-Workspace-ID"] = ws_id
    return headers, ws_id


def test_system_health_and_readiness() -> None:
    h = client.get("/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"

    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
    assert r.json()["database"] == "connected"


def test_auth_me_endpoint() -> None:
    headers, _ = get_authenticated_session()
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert "@example.test" in me.json()["email"]


def test_dataset_lifecycle_and_safe_query() -> None:
    headers, _ws_id = get_authenticated_session()

    # 1. Register dataset
    d_create = client.post(
        "/api/v1/datasets",
        json={"name": "Sales Q1", "description": "Q1 Orders", "source_type": "csv"},
        headers=headers,
    )
    assert d_create.status_code == 201
    dataset_id = d_create.json()["dataset_id"]

    # 2. List datasets
    d_list = client.get("/api/v1/datasets", headers=headers)
    assert d_list.status_code == 200
    assert any(d["dataset_id"] == dataset_id for d in d_list.json())

    # 3. Query dataset with safe SQL
    q_res = client.post(
        f"/api/v1/datasets/{dataset_id}/query",
        json={"query": "SELECT month, region, revenue FROM orders WHERE region = 'North'"},
        headers=headers,
    )
    assert q_res.status_code == 200
    assert q_res.json()["status"] == "success"
    assert len(q_res.json()["rows"]) > 0

    # 4. Reject unsafe mutation query
    bad_q = client.post(
        f"/api/v1/datasets/{dataset_id}/query",
        json={"query": "DELETE FROM orders WHERE region = 'North'"},
        headers=headers,
    )
    assert bad_q.status_code == 400


def test_document_upload_and_chunk_inspection() -> None:
    headers, _ws_id = get_authenticated_session()

    doc_file = io.BytesIO(b"Quarterly Business Review\nNorth revenue declined in March due to sales pipeline delays.")
    upload = client.post(
        "/api/v1/documents",
        files={"file": ("qbr_memo.txt", doc_file, "text/plain")},
        headers=headers,
    )
    assert upload.status_code == 200
    doc_id = upload.json()["document_id"]
    assert upload.json()["status"] == "indexed"

    # List documents
    docs = client.get("/api/v1/documents", headers=headers)
    assert docs.status_code == 200
    assert any(d["document_id"] == doc_id for d in docs.json())

    # Inspect chunks
    chunks = client.get(f"/api/v1/documents/{doc_id}/chunks", headers=headers)
    assert chunks.status_code == 200
    assert len(chunks.json()) > 0
    assert "pipeline delays" in chunks.json()[0]["text"]


def test_conversation_and_chat_messages() -> None:
    headers, _ws_id = get_authenticated_session()

    conv = client.post(
        "/api/v1/conversations",
        json={"title": "Q1 Performance Review"},
        headers=headers,
    )
    assert conv.status_code == 201
    conv_id = conv.json()["conversation_id"]

    msg = client.post(
        f"/api/v1/conversations/{conv_id}/messages?mode=multi",
        json={"content": "What was the revenue change from January to March?"},
        headers=headers,
    )
    assert msg.status_code == 200
    assert "revenue" in msg.json()["executive_summary"].lower()

    history = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 2  # user message and assistant reply


def test_investigation_and_opentelemetry_traces() -> None:
    headers, _ws_id = get_authenticated_session()

    inv = client.post(
        "/api/v1/investigations",
        json={"question": "Analyze North region performance divergence", "mode": "multi"},
        headers=headers,
    )
    assert inv.status_code == 200
    inv_id = inv.json()["investigation_id"]

    # Timeline steps
    tl = client.get(f"/api/v1/investigations/{inv_id}/timeline", headers=headers)
    assert tl.status_code == 200
    assert len(tl.json()) >= 5

    # Traces in OpenTelemetry format
    traces = client.get(f"/api/v1/investigations/{inv_id}/traces", headers=headers)
    assert traces.status_code == 200
    trace_data = traces.json()
    assert "trace_id" in trace_data
    assert "root_span" in trace_data
    assert len(trace_data["spans"]) >= 5


def test_evaluation_benchmark_run() -> None:
    headers, _ws_id = get_authenticated_session()

    bench = client.post(
        "/api/v1/evaluations/benchmark",
        json={"suite_name": "q1_accuracy_benchmark", "execution_mode": "comparison"},
        headers=headers,
    )
    assert bench.status_code == 200
    assert bench.json()["passed_cases"] == 10
    assert bench.json()["precision_at_k"] > 0.0

    runs = client.get("/api/v1/evaluations/runs", headers=headers)
    assert runs.status_code == 200
    assert len(runs.json()) > 0


def test_cross_workspace_isolation() -> None:
    # Workspace A
    headers_a, _ws_a = get_authenticated_session()
    doc_a = io.BytesIO(b"CONFIDENTIAL SECRET DOCUMENT FOR WORKSPACE A ONLY.")
    res_a = client.post(
        "/api/v1/documents",
        files={"file": ("secret_a.txt", doc_a, "text/plain")},
        headers=headers_a,
    )
    doc_id_a = res_a.json()["document_id"]

    # Workspace B
    headers_b, _ws_b = get_authenticated_session()

    # Workspace B should NOT see Workspace A's document chunks
    chunks_b = client.get(f"/api/v1/documents/{doc_id_a}/chunks", headers=headers_b)
    assert len(chunks_b.json()) == 0

    # Workspace B document listing should NOT contain doc_id_a
    docs_b = client.get("/api/v1/documents", headers=headers_b)
    assert all(d["document_id"] != doc_id_a for d in docs_b.json())
