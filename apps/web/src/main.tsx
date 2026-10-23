import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Report = { executive_summary: string; findings: { statement: string; status: string }[]; recommendations: { priority: number; action: string; rationale: string }[]; limitations: string[]; trace_id: string };

function App() {
  const [question, setQuestion] = useState("Revenue declined this quarter. Investigate the trend and recommend actions.");
  const [mode, setMode] = useState("single");
  const [workspace, setWorkspace] = useState("demo-workspace");
  const [report, setReport] = useState<Report>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function investigate() {
    setLoading(true); setError("");
    try {
      const response = await fetch("/api/v1/investigations", { method: "POST", headers: { "Content-Type": "application/json", "X-Workspace-ID": workspace }, body: JSON.stringify({ question, mode }) });
      if (!response.ok) throw new Error((await response.json()).detail || "Investigation failed");
      setReport(await response.json());
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Investigation failed"); }
    finally { setLoading(false); }
  }
  return <main><header><p className="eyebrow">BIZINTEL AI</p><h1>Decision intelligence, with evidence.</h1><p>Local demo mode uses synthetic business data and clearly labels its limitations.</p></header>
  <section className="panel"><label>Workspace<input value={workspace} onChange={e => setWorkspace(e.target.value)} /></label><label>Investigation question<textarea value={question} onChange={e => setQuestion(e.target.value)} /></label><label>Workflow<select value={mode} onChange={e => setMode(e.target.value)}><option value="single">Single agent</option><option value="multi">Supervisor workflow</option></select></label><button onClick={investigate} disabled={loading}>{loading ? "Investigating…" : "Start investigation"}</button>{error && <p className="error">{error}</p>}</section>
  {report && <section className="report"><p className="trace">Trace {report.trace_id}</p><h2>Executive summary</h2><p>{report.executive_summary}</p><h2>Findings</h2>{report.findings.map((f,i) => <article key={i}><span>{f.status}</span>{f.statement}</article>)}<h2>Prioritized actions</h2>{report.recommendations.map(r => <article key={r.priority}><strong>{r.priority}. {r.action}</strong><p>{r.rationale}</p></article>)}<h2>Limitations</h2><ul>{report.limitations.map(item => <li key={item}>{item}</li>)}</ul></section>}</main>;
}
createRoot(document.getElementById("root")!).render(<App />);
