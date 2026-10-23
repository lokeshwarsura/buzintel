from sqlalchemy import select

from backend.db.models import DocumentChunkRecord, StoredDocumentRecord, User, Workspace
from backend.db.session import Base, build_session_factory


def test_document_and_chunk_provenance_persist(tmp_path) -> None:
    factory, engine = build_session_factory(f"sqlite:///{tmp_path / 'documents.db'}")
    Base.metadata.create_all(engine)
    with factory.begin() as session:
        user = User(email="doc@example.test", password_hash="hash")
        session.add(user)
        session.flush()
        workspace = Workspace(name="Docs", owner_id=user.id)
        session.add(workspace)
        session.flush()
        document = StoredDocumentRecord(
            id="doc-1", workspace_id=workspace.id, name="report.md", content_hash="a" * 64
        )
        session.add(document)
        session.add(
            DocumentChunkRecord(
                id="doc:doc-1:0",
                document_id=document.id,
                chunk_index=0,
                source_location="text",
                text="Revenue declined",
            )
        )
    with factory() as session:
        assert session.scalar(select(DocumentChunkRecord.text)) == "Revenue declined"
