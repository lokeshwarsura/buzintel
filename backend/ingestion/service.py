"""Safe local document ingestion used until PostgreSQL/pgvector is provisioned."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from backend.models import Evidence

ALLOWED_SUFFIXES = {".txt", ".csv"}
MAX_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    workspace_id: str
    name: str
    content_hash: str
    text: str


class DocumentStore:
    def __init__(self) -> None:
        self._documents: dict[str, StoredDocument] = {}
        self._hashes: dict[tuple[str, str], str] = {}

    def ingest(self, workspace_id: str, name: str, content: bytes) -> StoredDocument:
        suffix = Path(name).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise ValueError("Only TXT and CSV are enabled in local demo mode.")
        if not content or len(content) > MAX_BYTES:
            raise ValueError("Document must be between 1 byte and 5 MiB.")
        digest = hashlib.sha256(content).hexdigest()
        existing = self._hashes.get((workspace_id, digest))
        if existing:
            return self._documents[existing]
        document = StoredDocument(
            str(uuid4()),
            workspace_id,
            Path(name).name,
            digest,
            content.decode("utf-8", errors="replace"),
        )
        self._documents[document.document_id] = document
        self._hashes[(workspace_id, digest)] = document.document_id
        return document

    def search(self, workspace_id: str, query: str, limit: int = 5) -> list[Evidence]:
        terms = {term.lower() for term in re.findall(r"[a-zA-Z0-9]+", query) if len(term) > 2}
        scored = []
        for document in self._documents.values():
            if document.workspace_id != workspace_id:
                continue
            text = document.text.lower()
            score = sum(text.count(term) for term in terms)
            if score:
                excerpt = document.text[:500].replace("\n", " ")
                scored.append(
                    (
                        score,
                        Evidence(
                            evidence_id=f"doc:{document.document_id}:0",
                            source_type="document",
                            title=document.name,
                            excerpt=excerpt,
                            source_ref=f"document:{document.document_id}",
                            workspace_id=workspace_id,
                        ),
                    )
                )
        return [
            evidence
            for _, evidence in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]
        ]

    def list(self, workspace_id: str) -> list[StoredDocument]:
        return [
            document
            for document in self._documents.values()
            if document.workspace_id == workspace_id
        ]


document_store = DocumentStore()
