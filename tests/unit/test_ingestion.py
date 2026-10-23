import pytest

from backend.ingestion.service import DocumentStore


def test_ingestion_is_idempotent_per_workspace() -> None:
    store = DocumentStore()
    first = store.ingest("alpha", "report.txt", b"North revenue declined")
    second = store.ingest("alpha", "renamed.txt", b"North revenue declined")
    assert first.document_id == second.document_id


def test_document_search_never_crosses_workspace_boundary() -> None:
    store = DocumentStore()
    store.ingest("alpha", "report.txt", b"North revenue declined")
    assert store.search("beta", "revenue") == []


def test_ingestion_rejects_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Supported"):
        DocumentStore().ingest("alpha", "report.exe", b"not a document")
