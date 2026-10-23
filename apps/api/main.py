"""HTTP entry point for BizIntel AI."""

from typing import Annotated

from fastapi import FastAPI, File, Header, HTTPException, UploadFile

from backend.agents.workflow import run_investigation
from backend.analytics.execution import metric_definitions
from backend.core.config import settings
from backend.ingestion.service import document_store
from backend.models import InvestigationReport, InvestigationRequest

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness endpoint; deliberately does not depend on external services."""
    return {"status": "ok", "service": "api"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    """Readiness placeholder until database dependency checks are introduced."""
    return {"status": "ready", "database": "not-configured"}


def workspace_context(x_workspace_id: str | None) -> str:
    if not x_workspace_id or len(x_workspace_id) > 64:
        raise HTTPException(status_code=401, detail="A valid X-Workspace-ID header is required.")
    return x_workspace_id


@app.get("/api/v1/metrics/definitions", tags=["analytics"])
def get_metric_definitions() -> dict[str, dict[str, str]]:
    return {"definitions": metric_definitions()}


@app.post("/api/v1/investigations", response_model=InvestigationReport, tags=["investigations"])
def create_investigation(
    request: InvestigationRequest, x_workspace_id: str | None = Header(default=None)
) -> InvestigationReport:
    return run_investigation(request, workspace_context(x_workspace_id))


@app.post("/api/v1/documents", tags=["documents"])
async def upload_document(
    file: Annotated[UploadFile, File()],
    x_workspace_id: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    try:
        document = document_store.ingest(
            workspace_context(x_workspace_id), file.filename or "upload.txt", await file.read()
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {
        "document_id": document.document_id,
        "status": "indexed",
        "content_hash": document.content_hash,
    }


@app.get("/api/v1/documents", tags=["documents"])
def list_documents(x_workspace_id: str | None = Header(default=None)) -> list[dict[str, str]]:
    return [
        {
            "document_id": item.document_id,
            "name": item.name,
            "content_hash": item.content_hash,
            "status": "indexed",
        }
        for item in document_store.list(workspace_context(x_workspace_id))
    ]
