"""Multi-format, workspace-isolated local RAG fallback with stable chunk provenance."""

import csv
import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import fitz
from docx import Document
from openpyxl import load_workbook

from backend.models import Evidence

ALLOWED_SUFFIXES = {".txt", ".md", ".csv", ".pdf", ".docx", ".xlsx"}
MAX_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    workspace_id: str
    name: str
    content_hash: str
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    index: int
    text: str
    source_location: str


def extract_text(name: str, content: bytes) -> tuple[str, list[str]]:
    suffix = Path(name).suffix.lower()
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8", errors="replace"), ["text"]
    if suffix == ".csv":
        rows = list(csv.reader(io.StringIO(content.decode("utf-8", errors="replace"))))
        return "\n".join(" | ".join(row) for row in rows), ["table"]
    if suffix == ".docx":
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs), ["document"]
    if suffix == ".xlsx":
        book = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        return "\n".join(
            " | ".join(str(v or "") for v in row)
            for sheet in book
            for row in sheet.iter_rows(values_only=True)
        ), list(book.sheetnames)
    if suffix == ".pdf":
        try:
            pdf = fitz.open(stream=content, filetype="pdf")
            return "\n".join(page.get_text() for page in pdf), [
                f"page:{i + 1}" for i in range(len(pdf))
            ]
        except Exception as error:
            raise ValueError("Document could not be parsed.") from error
    raise ValueError("Unsupported document type.")


class DocumentStore:
    def __init__(self) -> None:
        self._documents: dict[str, StoredDocument] = {}
        self._hashes: dict[tuple[str, str], str] = {}
        self._chunks: dict[str, list[DocumentChunk]] = {}

    def ingest(self, workspace_id: str, name: str, content: bytes) -> StoredDocument:
        if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError("Supported types: PDF, DOCX, TXT, MD, CSV and XLSX.")
        if not content or len(content) > MAX_BYTES:
            raise ValueError("Document must be between 1 byte and 5 MiB.")
        digest = hashlib.sha256(content).hexdigest()
        existing = self._hashes.get((workspace_id, digest))
        if existing:
            return self._documents[existing]
        text, locations = extract_text(name, content)
        document = StoredDocument(str(uuid4()), workspace_id, Path(name).name, digest, text)
        blocks = [text[i : i + 800] for i in range(0, len(text), 700)] or [""]
        self._chunks[document.document_id] = [
            DocumentChunk(
                f"doc:{document.document_id}:{i}",
                document.document_id,
                i,
                block,
                locations[min(i, len(locations) - 1)],
            )
            for i, block in enumerate(blocks)
        ]
        self._documents[document.document_id] = document
        self._hashes[(workspace_id, digest)] = document.document_id
        return document

    def search(self, workspace_id: str, query: str, limit: int = 5) -> list[Evidence]:
        terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        scored = []
        for doc in self._documents.values():
            if doc.workspace_id != workspace_id:
                continue
            for chunk in self._chunks[doc.document_id]:
                score = sum(chunk.text.lower().count(term) for term in terms if len(term) > 2)
                if score:
                    scored.append(
                        (
                            score,
                            Evidence(
                                evidence_id=chunk.chunk_id,
                                source_type="document",
                                title=doc.name,
                                excerpt=chunk.text[:500].replace("\n", " "),
                                source_ref=f"document:{doc.document_id}:{chunk.source_location}",
                                workspace_id=workspace_id,
                            ),
                        )
                    )
        return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]]

    def list(self, workspace_id: str) -> list[StoredDocument]:
        return [doc for doc in self._documents.values() if doc.workspace_id == workspace_id]


document_store = DocumentStore()
