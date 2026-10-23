import { useEffect, useState } from "react";
import { fetchDocumentChunks, fetchDocuments, uploadDocument, type DocumentChunkResponse, type DocumentResponse } from "../api";

interface Props {
  workspaceId: string;
}

export function KnowledgeBase({ workspaceId }: Props) {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [chunks, setChunks] = useState<DocumentChunkResponse[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      const list = await fetchDocuments(workspaceId);
      setDocuments(list);
      if (list.length > 0 && !selectedDocId) {
        setSelectedDocId(list[0].document_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    }
  }

  async function loadChunks(docId: string) {
    try {
      const chunkList = await fetchDocumentChunks(workspaceId, docId);
      setChunks(chunkList);
    } catch {
      setChunks([]);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, [workspaceId]);

  useEffect(() => {
    if (selectedDocId) {
      loadChunks(selectedDocId);
    }
  }, [selectedDocId, workspaceId]);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg("");
    setError("");

    try {
      const doc = await uploadDocument(workspaceId, file);
      setUploadMsg(`Successfully indexed "${doc.name}" with hash ${doc.content_hash.slice(0, 8)}…`);
      await loadDocuments();
      setSelectedDocId(doc.document_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Knowledge Base & Multi-Format Ingestion</h1>
          <p className="page-description">
            Workspace-isolated RAG storage with hybrid vector retrieval, stable chunk provenance, and prompt-injection defense.
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <label className="btn btn-primary" style={{ cursor: "pointer" }}>
            <span>{uploading ? "Ingesting & Chunking…" : "Upload Business Document"}</span>
            <input
              type="file"
              style={{ display: "none" }}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.txt,.md,.csv,.xlsx"
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      {uploadMsg && (
        <div style={{ marginBottom: "20px", padding: "12px", background: "rgba(16, 185, 129, 0.1)", borderRadius: "8px", border: "1px solid var(--accent-emerald)", color: "#6ee7b7", fontSize: "13px" }}>
          ✓ {uploadMsg}
        </div>
      )}

      {error && (
        <div style={{ marginBottom: "20px", padding: "12px", background: "rgba(244, 63, 94, 0.1)", borderRadius: "8px", border: "1px solid var(--accent-rose)", color: "#fda4af", fontSize: "13px" }}>
          {error}
        </div>
      )}

      {/* Main Grid: Document List & Chunk Inspector */}
      <div className="grid-2">
        {/* Document Inventory */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Indexed Documents ({documents.length})</h3>
            <span className="badge badge-blue">Supported: PDF, DOCX, TXT, MD, CSV, XLSX</span>
          </div>

          {documents.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)", fontSize: "14px" }}>
              No documents in this workspace yet. Upload a corporate report, sales memo, or spreadsheet.
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Content Hash</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((d) => (
                    <tr
                      key={d.document_id}
                      style={{
                        background: selectedDocId === d.document_id ? "rgba(59, 130, 246, 0.1)" : undefined,
                        cursor: "pointer",
                      }}
                      onClick={() => setSelectedDocId(d.document_id)}
                    >
                      <td>
                        <strong style={{ color: selectedDocId === d.document_id ? "var(--accent-cyan)" : "#fff" }}>
                          {d.name}
                        </strong>
                      </td>
                      <td>
                        <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                          {d.content_hash.slice(0, 10)}…
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-emerald">{d.status}</span>
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: "11px", padding: "4px 8px" }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedDocId(d.document_id);
                          }}
                        >
                          View Chunks
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div style={{ marginTop: "20px", padding: "12px", background: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <h4 style={{ fontSize: "12px", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "4px" }}>
              Security & Injection Protection
            </h4>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              All ingested files undergo SHA-256 deduplication and automatic token sanitization. Injection delimiters like <code>&lt;|system|&gt;</code> and <code>ignore previous instructions</code> are neutralized at retrieval time.
            </p>
          </div>
        </div>

        {/* Chunk Inspector */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>
              Chunk Provenance Inspector ({chunks.length} Chunks)
            </h3>
            <span className="badge badge-purple">Provenance Verified</span>
          </div>

          {!selectedDocId ? (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)", fontSize: "14px" }}>
              Select a document to inspect its chunk boundaries and source citations.
            </div>
          ) : chunks.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)", fontSize: "14px" }}>
              No chunk records found for this document.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", maxHeight: "550px", overflowY: "auto" }}>
              {chunks.map((c) => (
                <div
                  key={c.chunk_id}
                  style={{
                    padding: "14px",
                    background: "rgba(0, 0, 0, 0.3)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>
                      {c.chunk_id}
                    </span>
                    <span className="badge badge-blue">Location: {c.source_location}</span>
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--text-primary)", lineHeight: 1.5 }}>{c.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
