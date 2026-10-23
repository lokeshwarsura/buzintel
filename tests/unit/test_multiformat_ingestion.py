from docx import Document

from backend.ingestion.service import DocumentStore


def test_markdown_chunks_have_stable_provenance() -> None:
    store = DocumentStore()
    document = store.ingest("a", "report.md", b"# Revenue\nNorth revenue fell")
    result = store.search("a", "north revenue")
    assert result and result[0].evidence_id.startswith(f"doc:{document.document_id}:")


def test_docx_is_searchable() -> None:
    document = Document()
    document.add_paragraph("Marketing spend increased")
    path = __import__("io").BytesIO()
    document.save(path)
    store = DocumentStore()
    store.ingest("a", "report.docx", path.getvalue())
    assert store.search("a", "marketing")
