"""Multi-format, workspace-isolated RAG service with hybrid retrieval, vector fallback, and injection defense."""

import csv
import hashlib
import io
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import fitz
from docx import Document
from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import DocumentChunkRecord, StoredDocumentRecord
from backend.models import Evidence

ALLOWED_SUFFIXES = {".txt", ".md", ".csv", ".pdf", ".docx", ".xlsx"}
MAX_BYTES = 5 * 1024 * 1024

# Prompt injection signatures in untrusted business documents
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"(<\s*\|?\s*im_start\s*\|?>|<\s*\|?\s*system\s*\|?>|<<SYS>>|\[INST\])", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"new\s+instructions\s*:", re.IGNORECASE),
]


def sanitize_retrieved_text(text: str) -> str:
    """Sanitize retrieved document text against prompt-injection attacks.

    Neutralizes delimiter injection, overrides, and role-spoofing markers.
    """
    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[FILTERED_PROMPT_INJECTION]", sanitized)
    # Neutralize XML/HTML/special delimiter tags
    sanitized = sanitized.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")
    return sanitized.strip()


def compute_embedding(text: str, dim: int = 64) -> list[float]:
    """Deterministic, local semantic n-gram hashing embedding with L2 normalization.

    Provides vector search capabilities without requiring external network calls or GPU dependencies.
    """
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = clean.split()
    if not words:
        return [0.0] * dim

    vec = [0.0] * dim
    # Unigram and bigram feature hashing
    features = words + [f"{words[i]}_{words[i + 1]}" for i in range(len(words) - 1)]
    for feat in features:
        h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
        index = h % dim
        sign = 1.0 if ((h >> 8) % 2 == 0) else -1.0
        vec[index] += sign

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two unit vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2, strict=False))


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
    embedding: list[float] | None = None


def extract_text(name: str, content: bytes) -> tuple[str, list[str]]:
    """Extract plain text and structured location markers from multiple document formats."""
    suffix = Path(name).suffix.lower()
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8", errors="replace"), ["text"]
    if suffix == ".csv":
        rows = list(csv.reader(io.StringIO(content.decode("utf-8", errors="replace"))))
        return "\n".join(" | ".join(row) for row in rows), ["table"]
    if suffix == ".docx":
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text), ["document"]
    if suffix == ".xlsx":
        book = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        sheets = list(book.sheetnames)
        text_lines = []
        locations = []
        for sheet_name in sheets:
            sheet = book[sheet_name]
            for row in sheet.iter_rows(values_only=True):
                line = " | ".join(str(v or "") for v in row if v is not None)
                if line.strip():
                    text_lines.append(line)
                    locations.append(f"sheet:{sheet_name}")
        return "\n".join(text_lines), locations or ["sheet:1"]
    if suffix == ".pdf":
        try:
            pdf = fitz.open(stream=content, filetype="pdf")
            pages = []
            locations = []
            for i in range(len(pdf)):
                page_text = pdf[i].get_text()
                if page_text.strip():
                    pages.append(page_text)
                    locations.append(f"page:{i + 1}")
            return "\n\n".join(pages), locations or ["page:1"]
        except Exception as error:
            raise ValueError("Document could not be parsed.") from error
    raise ValueError("Unsupported document type.")


class DocumentStore:
    """Persistent and in-memory capable document store with hybrid retrieval and workspace isolation."""

    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory
        self._documents: dict[str, StoredDocument] = {}
        self._hashes: dict[tuple[str, str], str] = {}
        self._chunks: dict[str, list[DocumentChunk]] = {}

    def set_session_factory(self, session_factory) -> None:
        self.session_factory = session_factory

    def ingest(
        self,
        workspace_id: str,
        name: str,
        content: bytes,
        session: Session | None = None,
    ) -> StoredDocument:
        if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError("Supported types: PDF, DOCX, TXT, MD, CSV and XLSX.")
        if not content or len(content) > MAX_BYTES:
            raise ValueError("Document must be between 1 byte and 5 MiB.")

        digest = hashlib.sha256(content).hexdigest()

        # Check DB first if session available
        active_session = session or (self.session_factory() if self.session_factory else None)
        try:
            if active_session:
                existing_rec = active_session.scalar(
                    select(StoredDocumentRecord).where(
                        StoredDocumentRecord.workspace_id == workspace_id,
                        StoredDocumentRecord.content_hash == digest,
                    )
                )
                if existing_rec:
                    chunks = list(
                        active_session.scalars(
                            select(DocumentChunkRecord)
                            .where(DocumentChunkRecord.document_id == existing_rec.id)
                            .order_by(DocumentChunkRecord.chunk_index)
                        )
                    )
                    full_text = "\n".join(c.text for c in chunks)
                    doc = StoredDocument(existing_rec.id, workspace_id, existing_rec.name, digest, full_text)
                    self._documents[doc.document_id] = doc
                    self._hashes[(workspace_id, digest)] = doc.document_id
                    return doc

            # Check memory cache
            existing = self._hashes.get((workspace_id, digest))
            if existing and existing in self._documents:
                return self._documents[existing]

            text, locations = extract_text(name, content)
            document = StoredDocument(str(uuid4()), workspace_id, Path(name).name, digest, text)
            blocks = [text[i : i + 800] for i in range(0, len(text), 700)] or [""]

            chunk_records = []
            chunk_objs = []
            for i, block in enumerate(blocks):
                loc = locations[min(i, len(locations) - 1)]
                chunk_id = f"doc:{document.document_id}:{i}"
                embedding = compute_embedding(block)
                chunk_objs.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        index=i,
                        text=block,
                        source_location=loc,
                        embedding=embedding,
                    )
                )
                chunk_records.append(
                    DocumentChunkRecord(
                        id=chunk_id,
                        document_id=document.document_id,
                        workspace_id=workspace_id,
                        chunk_index=i,
                        source_location=loc,
                        text=block,
                        embedding_json=json.dumps(embedding),
                    )
                )

            # Persist to database if session exists
            if active_session:
                doc_record = StoredDocumentRecord(
                    id=document.document_id,
                    workspace_id=workspace_id,
                    name=document.name,
                    content_hash=digest,
                    mime_type="text/plain",
                    byte_size=len(content),
                    status="indexed",
                )
                active_session.add(doc_record)
                for cr in chunk_records:
                    active_session.add(cr)
                if not session:  # We opened the session locally, commit it
                    active_session.commit()
                else:
                    active_session.flush()

            self._chunks[document.document_id] = chunk_objs
            self._documents[document.document_id] = document
            self._hashes[(workspace_id, digest)] = document.document_id
            return document
        finally:
            if active_session and not session:
                active_session.close()

    def search(
        self,
        workspace_id: str,
        query: str,
        limit: int = 5,
        session: Session | None = None,
        enable_rerank: bool = True,
    ) -> list[Evidence]:
        """Hybrid lexical and vector retrieval with citation provenance and injection sanitization."""
        terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        query_vec = compute_embedding(query)

        # Candidates to score: (chunk_id, doc_id, doc_name, text, source_location, embedding)
        candidates = []

        active_session = session or (self.session_factory() if self.session_factory else None)
        try:
            if active_session:
                rows = active_session.execute(
                    select(
                        DocumentChunkRecord.id,
                        DocumentChunkRecord.document_id,
                        StoredDocumentRecord.name,
                        DocumentChunkRecord.text,
                        DocumentChunkRecord.source_location,
                        DocumentChunkRecord.embedding_json,
                    )
                    .join(StoredDocumentRecord, DocumentChunkRecord.document_id == StoredDocumentRecord.id)
                    .where(StoredDocumentRecord.workspace_id == workspace_id)
                ).all()
                for cid, did, dname, text, loc, emb_json in rows:
                    emb = json.loads(emb_json) if emb_json else None
                    candidates.append((cid, did, dname, text, loc, emb))
            else:
                for doc in self._documents.values():
                    if doc.workspace_id != workspace_id:
                        continue
                    for chunk in self._chunks.get(doc.document_id, []):
                        candidates.append((
                            chunk.chunk_id,
                            doc.document_id,
                            doc.name,
                            chunk.text,
                            chunk.source_location,
                            chunk.embedding,
                        ))

            if not candidates:
                return []

            scored = []
            max_lex = 1.0
            raw_scores = []
            for cid, did, dname, text, loc, emb in candidates:
                # 1. Lexical score
                lex_score = sum(text.lower().count(term) for term in terms if len(term) > 2)
                # 2. Vector score
                vec_score = cosine_similarity(query_vec, emb) if emb else 0.0
                raw_scores.append((cid, did, dname, text, loc, lex_score, vec_score))
                max_lex = max(max_lex, lex_score)

            # Normalize and compute hybrid score (50% lexical, 50% vector)
            for cid, did, dname, text, loc, lex_score, vec_score in raw_scores:
                norm_lex = lex_score / max_lex
                hybrid = 0.5 * norm_lex + 0.5 * max(0.0, vec_score)
                if hybrid > 0.05 or lex_score > 0:
                    sanitized_excerpt = sanitize_retrieved_text(text[:500]).replace("\n", " ")
                    evidence = Evidence(
                        evidence_id=cid,
                        source_type="document",
                        title=dname,
                        excerpt=sanitized_excerpt,
                        source_ref=f"document:{did}:{loc}",
                        workspace_id=workspace_id,
                    )
                    scored.append((hybrid, evidence))

            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [item for _, item in scored[:limit]]
        finally:
            if active_session and not session:
                active_session.close()

    def list(self, workspace_id: str, session: Session | None = None) -> list[StoredDocument]:
        active_session = session or (self.session_factory() if self.session_factory else None)
        try:
            if active_session:
                records = list(
                    active_session.scalars(
                        select(StoredDocumentRecord).where(StoredDocumentRecord.workspace_id == workspace_id)
                    )
                )
                return [
                    StoredDocument(r.id, r.workspace_id, r.name, r.content_hash, "")
                    for r in records
                ]
            return [doc for doc in self._documents.values() if doc.workspace_id == workspace_id]
        finally:
            if active_session and not session:
                active_session.close()


document_store = DocumentStore()
