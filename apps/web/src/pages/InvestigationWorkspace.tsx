import { useState } from "react";
import { createInvestigation, fetchInvestigationTimeline, type AgentRunResponse, type InvestigationReport } from "../api";

interface Props {
  workspaceId: string;
  initialQuestion?: string;
  onViewTrace: (investigationId: string) => void;
}

export function InvestigationWorkspace({ workspaceId, initialQuestion, onViewTrace }: Props) {
  const [question, setQuestion] = useState(
    initialQuestion || "Revenue declined by 15% this quarter. Compare regions and product categories, inspect relevant business documents, identify evidence-supported explanations, and recommend three prioritized actions."
  );
  const [mode, setMode] = useState<"single" | "multi">("multi");
  const [reportingPeriod, setReportingPeriod] = useState("2026-01 to 2026-03");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<InvestigationReport | null>(null);
  const [timeline, setTimeline] = useState<AgentRunResponse[]>([]);

  async function handleInvestigate() {
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    setReport(null);
    setTimeline([]);

    try {
      const result = await createInvestigation(workspaceId, question, mode, reportingPeriod);
      setReport(result);

      // Fetch persistent timeline steps if available
      try {
        const steps = await fetchInvestigationTimeline(workspaceId, result.investigation_id);
        setTimeline(steps);
      } catch {
        // Timeline fetch optional
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Investigation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Investigation Workspace</h1>
          <p className="page-description">
            Hierarchical multi-agent root-cause discovery with verified calculations and strict citation standards.
          </p>
        </div>
      </div>

      {/* Input Panel */}
      <div className="card" style={{ marginBottom: "28px" }}>
        <div style={{ marginBottom: "16px" }}>
          <label style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
            Investigation Question or Commercial Hypothesis
          </label>
          <textarea
            className="textarea"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Why did Q1 revenue decline in North region?"
          />
        </div>

        {/* Quick presets */}
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "16px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", alignSelf: "center" }}>Presets:</span>
          <button
            className="badge badge-blue"
            style={{ cursor: "pointer", border: "1px solid rgba(59,130,246,0.3)" }}
            onClick={() => setQuestion("Revenue declined this quarter. Compare regions and categories, inspect documents, and recommend 3 actions.")}
          >
            Q1 Regional Revenue Decline
          </button>
          <button
            className="badge badge-purple"
            style={{ cursor: "pointer", border: "1px solid rgba(139,92,246,0.3)" }}
            onClick={() => setQuestion("Evaluate North region target achievement and audit marketing search ad spend changes.")}
          >
            North Target & Ad Spend Audit
          </button>
          <button
            className="badge badge-emerald"
            style={{ cursor: "pointer", border: "1px solid rgba(16,185,129,0.3)" }}
            onClick={() => setQuestion("Calculate gross margins and protect profitability constraints before promotional discounting.")}
          >
            Margin Constraint Protection
          </button>
        </div>

        <div style={{ display: "flex", gap: "16px", alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ width: "240px" }}>
            <label style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
              Orchestration Mode
            </label>
            <select className="select" value={mode} onChange={(e) => setMode(e.target.value as "single" | "multi")}>
              <option value="multi">Hierarchical Multi-Agent (6 Specialists)</option>
              <option value="single">Single Agent (Fast Bounded Workflow)</option>
            </select>
          </div>

          <div style={{ width: "200px" }}>
            <label style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
              Reporting Period
            </label>
            <input className="input" value={reportingPeriod} onChange={(e) => setReportingPeriod(e.target.value)} />
          </div>

          <div style={{ marginLeft: "auto", alignSelf: "flex-end" }}>
            <button className="btn btn-primary" onClick={handleInvestigate} disabled={loading}>
              {loading ? (
                <>
                  <span className="pulse">●</span>
                  <span>Specialists Analyzing…</span>
                </>
              ) : (
                <span>Launch Investigation</span>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: "16px", padding: "12px", background: "rgba(244, 63, 94, 0.1)", borderRadius: "8px", border: "1px solid var(--accent-rose)", color: "#fda4af", fontSize: "13px" }}>
            {error}
          </div>
        )}
      </div>

      {/* Specialist Step Timeline */}
      {mode === "multi" && (loading || timeline.length > 0) && (
        <div className="card" style={{ marginBottom: "28px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>Specialist Execution Timeline</span>
            <span className="badge badge-cyan">{timeline.length} Steps</span>
          </h3>

          <div style={{ paddingLeft: "8px" }}>
            {timeline.length > 0 ? (
              timeline.map((step) => (
                <div key={step.run_id} className="step-item">
                  <div className="step-icon">{step.step_number}</div>
                  <div className="step-body">
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span className="step-role">{step.agent_role.replace(/_/g, " ").toUpperCase()}</span>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>{step.duration_ms} ms</span>
                    </div>
                    {step.details && (
                      <div className="step-action">
                        {(() => {
                          try {
                            const d = JSON.parse(step.details);
                            return d.action || d.details || step.details;
                          } catch {
                            return step.details;
                          }
                        })()}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                1. Supervisor/Planner → 2. Metric Analyst → 3. Document Researcher → 4. Trend Analyst → 5. Evidence Critic → 6. Report Synthesizer
              </div>
            )}
          </div>
        </div>
      )}

      {/* Investigation Report Results */}
      {report && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Executive Summary */}
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span className="badge badge-emerald">Investigation Complete</span>
                <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  Period: {report.reporting_period}
                </span>
              </div>
              <button
                className="btn btn-secondary"
                style={{ fontSize: "12px", padding: "6px 12px" }}
                onClick={() => onViewTrace(report.investigation_id)}
              >
                Inspect Trace ({report.trace_id.slice(0, 8)}…)
              </button>
            </div>

            <h2 style={{ fontSize: "18px", fontWeight: 700, marginBottom: "8px" }}>Executive Summary</h2>
            <p style={{ fontSize: "15px", lineHeight: 1.6, color: "#e2e8f0" }}>{report.executive_summary}</p>
          </div>

          {/* Findings: Confirmed vs Hypotheses */}
          <div className="card">
            <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "14px" }}>
              Evidence-Backed Findings & Hypotheses
            </h3>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "16px" }}>
              BizIntel strictly separates verified observations from unproven causal hypotheses to avoid hallucination.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {report.findings.map((f, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "14px 16px",
                    borderRadius: "8px",
                    background: f.status === "confirmed" ? "rgba(16, 185, 129, 0.05)" : "rgba(245, 158, 11, 0.05)",
                    border: `1px solid ${f.status === "confirmed" ? "rgba(16, 185, 129, 0.2)" : "rgba(245, 158, 11, 0.2)"}`,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                    <span className={f.status === "confirmed" ? "badge badge-emerald" : "badge badge-amber"}>
                      {f.status === "confirmed" ? "VERIFIED OBSERVATION" : "HYPOTHESIS"}
                    </span>
                    {f.evidence_ids.map((eid) => (
                      <span key={eid} style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                        [{eid}]
                      </span>
                    ))}
                  </div>
                  <p style={{ fontSize: "14px", color: "var(--text-primary)" }}>{f.statement}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Prioritized Actions */}
          <div className="card">
            <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "14px" }}>
              Prioritized Commercial Recommendations
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
              {report.recommendations.map((r) => (
                <div
                  key={r.priority}
                  style={{
                    padding: "16px",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "10px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <span className="badge badge-purple">Priority {r.priority}</span>
                  </div>
                  <h4 style={{ fontSize: "14px", fontWeight: 700, marginBottom: "8px", color: "#fff" }}>{r.action}</h4>
                  <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>{r.rationale}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Evidence Citations & Limitations */}
          <div className="grid-2">
            <div className="card">
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "12px" }}>
                Cited Evidence & Provenance ({report.citations.length})
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "300px", overflowY: "auto" }}>
                {report.citations.map((c) => (
                  <div
                    key={c.evidence_id}
                    style={{
                      padding: "10px 12px",
                      background: "rgba(0,0,0,0.3)",
                      borderRadius: "6px",
                      border: "1px solid var(--border-color)",
                      fontSize: "12px",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                      <span style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>{c.title}</span>
                      <span className={c.source_type === "metric" ? "badge badge-blue" : "badge badge-purple"}>
                        {c.source_type}
                      </span>
                    </div>
                    <p style={{ color: "var(--text-secondary)", marginBottom: "4px" }}>{c.excerpt}</p>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                      Ref: {c.source_ref}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "12px" }}>
                Governance & Methodological Limitations
              </h3>
              <ul style={{ paddingLeft: "20px", display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px", color: "var(--text-secondary)" }}>
                {report.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>

              <div style={{ marginTop: "20px", padding: "12px", background: "rgba(59, 130, 246, 0.06)", borderRadius: "8px", border: "1px solid rgba(59, 130, 246, 0.2)" }}>
                <p style={{ fontSize: "12px", color: "#93c5fd" }}>
                  🔒 <strong>Governance Standard:</strong> No causal assertion is made from correlation alone. All numerical statements derive from certified AST-validated queries.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
