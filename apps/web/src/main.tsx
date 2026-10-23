import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { fetchReadiness } from "./api";
import { Dashboard } from "./pages/Dashboard";
import { EvaluationLab } from "./pages/EvaluationLab";
import { InvestigationWorkspace } from "./pages/InvestigationWorkspace";
import { KnowledgeBase } from "./pages/KnowledgeBase";
import { TraceViewer } from "./pages/TraceViewer";
import "./styles.css";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [workspaceId, setWorkspaceId] = useState("default");
  const [prefilledQuestion, setPrefilledQuestion] = useState<string | undefined>();
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [dbStatus, setDbStatus] = useState("checking");

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetchReadiness();
        setDbStatus(res.database === "connected" ? "connected" : "ready");
      } catch {
        setDbStatus("offline");
      }
    }
    checkHealth();
  }, []);

  function handleNavigate(tab: string, question?: string) {
    if (question) {
      setPrefilledQuestion(question);
    }
    setActiveTab(tab);
  }

  function handleViewTrace(investigationId: string) {
    setSelectedTraceId(investigationId);
    setActiveTab("trace");
  }

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-logo">BI</div>
          <div>
            <div className="brand-title">BizIntel AI</div>
            <div className="brand-subtitle">Decision Intelligence</div>
          </div>
        </div>

        <nav className="nav-menu">
          <button
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <span>📊</span>
            <span>Executive Dashboard</span>
          </button>

          <button
            className={`nav-item ${activeTab === "investigation" ? "active" : ""}`}
            onClick={() => setActiveTab("investigation")}
          >
            <span>🔍</span>
            <span>AI Investigation</span>
          </button>

          <button
            className={`nav-item ${activeTab === "knowledge" ? "active" : ""}`}
            onClick={() => setActiveTab("knowledge")}
          >
            <span>📚</span>
            <span>Knowledge Base</span>
          </button>

          <button
            className={`nav-item ${activeTab === "trace" ? "active" : ""}`}
            onClick={() => setActiveTab("trace")}
          >
            <span>⚡</span>
            <span>Agent Trace Viewer</span>
          </button>

          <button
            className={`nav-item ${activeTab === "evaluation" ? "active" : ""}`}
            onClick={() => setActiveTab("evaluation")}
          >
            <span>🧪</span>
            <span>Evaluation Laboratory</span>
          </button>
        </nav>

        {/* Workspace & System Indicator */}
        <div className="workspace-badge">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="workspace-badge-label">Active Workspace</span>
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: dbStatus === "connected" ? "var(--accent-emerald)" : "var(--accent-amber)",
              }}
              title={`Database status: ${dbStatus}`}
            />
          </div>
          <div className="workspace-badge-name">{workspaceId}</div>
          <input
            className="input"
            style={{ fontSize: "11px", padding: "4px 8px", marginTop: "8px" }}
            value={workspaceId}
            onChange={(e) => setWorkspaceId(e.target.value.trim() || "default")}
            placeholder="Switch Workspace"
          />
        </div>
      </aside>

      {/* Main Page Content */}
      <main className="main-content">
        {activeTab === "dashboard" && (
          <Dashboard workspaceId={workspaceId} onNavigate={handleNavigate} />
        )}

        {activeTab === "investigation" && (
          <InvestigationWorkspace
            workspaceId={workspaceId}
            initialQuestion={prefilledQuestion}
            onViewTrace={handleViewTrace}
          />
        )}

        {activeTab === "knowledge" && (
          <KnowledgeBase workspaceId={workspaceId} />
        )}

        {activeTab === "trace" && (
          <TraceViewer
            workspaceId={workspaceId}
            selectedInvestigationId={selectedTraceId}
          />
        )}

        {activeTab === "evaluation" && (
          <EvaluationLab workspaceId={workspaceId} />
        )}
      </main>
    </div>
  );
}

const rootEl = document.getElementById("root");
if (rootEl) {
  createRoot(rootEl).render(<App />);
}
