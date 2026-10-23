from fastapi.testclient import TestClient

from apps.api.main import app


def test_register_login_and_workspace_lifecycle() -> None:
    client = TestClient(app)
    credentials = {"email": "new-user@example.test", "password": "long-and-safe-password"}
    assert client.post("/api/v1/auth/register", json=credentials).status_code == 201
    token = client.post("/api/v1/auth/login", json=credentials).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/v1/workspaces", json={"name": "Analytics"}, headers=headers).status_code == 201
    assert len(client.get("/api/v1/workspaces", headers=headers).json()) == 1
