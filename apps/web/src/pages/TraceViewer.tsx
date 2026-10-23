import { useEffect, useState } from "react";
import { fetchInvestigations, fetchInvestigationTraces, type TraceData } from "../api";

interface Props {
  workspaceId: string;
  selectedInvestigationId?: string | null;
}

export function TraceViewer({ workspaceId, selectedInvestigationId }: Props) {
  const [investigations, setInvestigations] = useState<Array<{ investigation_id: string; question: string; execution_mode: string; status: string; created_at: string }>>([]);
  const [activeId, setActiveId] = useState<string | null>(selectedInvestigationId || null);
  const [trace, setTrace] = useState<TraceData | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<TraceData["spans"][0] | null>(null);
  const [loading, setLoading] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  useEffect(() => {
    async function loadList() {
      try {
        const list = await fetchInvestigations(workspaceId);
        setInvestigations(list);
        if (list.length > 0 && !activeId) {
          setActiveId(list[0].investigation_id);
        }
      } catch {
        // Handle error silently
      }
    }
    loadList();
  }, [workspaceId]);

  useEffect(() => {
    if (selectedInvestigationId) {
      setActiveId(selectedInvestigationId);
    }
  }, [selectedInvestigationId]);

  useEffect(() => {
    async function loadTrace() {
      if (!activeId) return;
      setLoading(true);
      try {
        const data = await fetchInvestigationTraces(workspaceId, activeId);
        setTrace(data);
        if (data.spans.length > 0) {
          setSelectedSpan(data.spans[0]);
        }
      } catch {
        setTrace(null);
      } finally {
        setLoading(false);
      }
    }
    loadTrace();
  }, [activeId, workspaceId]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Agent Trace & Observability Viewer</h1>
          <p className="page-description">
            OpenTelemetry-compatible timeline breakdown of specialist agent steps, tool calls, latency, and sanitized payloads.
          </p>
        </div>
        <div>
          <button
            className="btn btn-secondary"
            onClick={() => setShowRawJson(!showRawJson)}
            disabled={!trace}
          >
            {showRawJson ? "View Visual Spans" : "View OpenTelemetry JSON"}
          </button>
        </div>
      </div>

      <div className="grid-3" style={{ gridTemplateColumns: "320px 1fr 1fr", gap: "20px" }}>
        {/* Past Investigations Sidebar */}
        <div className="card" style={{ height: "fit-content" }}>
          <h3 style={{ fontSize: "14px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "12px" }}>
            Investigation Traces
          </h3>

          {investigations.length === 0 ? (
            <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>
              No traces recorded yet. Run an investigation to generate execution traces.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "500px", overflowY: "auto" }}>
              {investigations.map((inv) => (
                <div
                  key={inv.investigation_id}
                  style={{
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: activeId === inv.investigation_id ? "rgba(59, 130, 246, 0.15)" : "rgba(255,255,255,0.02)",
                    border: `1px solid ${activeId === inv.investigation_id ? "var(--accent-blue)" : "var(--border-color)"}`,
                    cursor: "pointer",
                  }}
                  onClick={() => setActiveId(inv.investigation_id)}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span className="badge badge-purple">{inv.execution_mode}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      {new Date(inv.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p style={{ fontSize: "13px", color: "#fff", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {inv.question}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Trace Timeline & Spans */}
        <div className="card" style={{ gridColumn: showRawJson ? "span 2" : "auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Execution Trace Tree</h3>
            {trace && <span className="badge badge-blue">Trace ID: {trace.trace_id.slice(0, 8)}…</span>}
          </div>

          {loading ? (
            <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)" }}>Loading trace spans…</div>
          ) : !trace ? (
            <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)" }}>Select a trace to inspect.</div>
          ) : showRawJson ? (
            <div className="code-block" style={{ maxHeight: "500px", overflowY: "auto" }}>
              <pre>{JSON.stringify(trace, null, 2)}</pre>
            </div>
          ) : (
            <div>
              {/* Root span */}
              <div
                style={{
                  padding: "12px",
                  background: "rgba(59, 130, 246, 0.1)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  borderRadius: "8px",
                  marginBottom: "16px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 700, color: "var(--accent-cyan)", fontSize: "13px" }}>
                    ● {trace.root_span.name}
                  </span>
                  <span className="badge badge-emerald">{trace.root_span.status}</span>
                </div>
                <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                  ID: {trace.root_span.investigation_id}
                </div>
              </div>

              {/* Child spans */}
              <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "400px", overflowY: "auto" }}>
                {trace.spans.map((span) => (
                  <div
                    key={span.span_id}
                    style={{
                      padding: "10px 14px",
                      borderRadius: "8px",
                      background: selectedSpan?.span_id === span.span_id ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.3)",
                      border: `1px solid ${selectedSpan?.span_id === span.span_id ? "var(--accent-blue)" : "var(--border-color)"}`,
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                    onClick={() => setSelectedSpan(span)}
                  >
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "13px", fontWeight: 600, color: span.name.startsWith("agent") ? "var(--accent-cyan)" : "var(--accent-purple)" }}>
                          {span.name}
                        </span>
                        <span className="badge badge-emerald">{span.status}</span>
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                        {span.span_id.slice(0, 10)}…
                      </div>
                    </div>
                    <div style={{ fontSize: "12px", fontWeight: 700, color: "#fff" }}>
                      {span.duration_ms} ms
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Selected Span Details */}
        {!showRawJson && (
          <div className="card">
            <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "16px" }}>Span Attributes</h3>

            {!selectedSpan ? (
              <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>Select a span from the trace tree.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div>
                  <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600 }}>Span Name</span>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--accent-cyan)" }}>{selectedSpan.name}</div>
                </div>

                <div>
                  <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600 }}>Latency</span>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "#fff" }}>{selectedSpan.duration_ms} milliseconds</div>
                </div>

                <div>
                  <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600 }}>Start Time</span>
                  <div style={{ fontSize: "12px", fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>{selectedSpan.start_time}</div>
                </div>

                <div>
                  <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600 }}>Attributes & Secret Redaction</span>
                  <div className="code-block" style={{ marginTop: "6px", maxHeight: "250px", overflowY: "auto" }}>
                    <pre>{JSON.stringify(selectedSpan.attributes, null, 2)}</pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
