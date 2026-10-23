import { useEffect, useState } from "react";
import { queryDataset } from "../api";

interface Props {
  workspaceId: string;
  onNavigate: (tab: string, question?: string) => void;
}

export function Dashboard({ workspaceId, onNavigate }: Props) {
  const [sqlQuery, setSqlQuery] = useState("SELECT region, SUM(revenue) AS total_revenue, SUM(cogs) AS total_cogs, SUM(orders_count) AS orders FROM orders GROUP BY region");
  const [sqlResult, setSqlResult] = useState<Array<Record<string, unknown>>>([]);
  const [sqlLoading, setSqlLoading] = useState(false);
  const [sqlError, setSqlError] = useState("");

  async function runQuery() {
    setSqlLoading(true);
    setSqlError("");
    try {
      const res = await queryDataset(workspaceId, "sales", sqlQuery);
      setSqlResult(res.rows);
    } catch (err) {
      setSqlError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setSqlLoading(false);
    }
  }

  useEffect(() => {
    runQuery();
  }, [workspaceId]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Analytics Dashboard</h1>
          <p className="page-description">
            Continuous financial and operational intelligence backed by verified semantic metrics.
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => onNavigate("investigation", "Why did North region revenue decline 17% in March?")}
        >
          <span>✨ New AI Investigation</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid-4" style={{ marginBottom: "28px" }}>
        <div className="card">
          <div className="kpi-title">Q1 2026 Revenue</div>
          <div className="kpi-value">$641,000.00</div>
          <div className="kpi-delta negative">
            <span>↓ -7.27%</span>
            <span style={{ color: "var(--text-muted)", marginLeft: "4px" }}>vs Jan baseline</span>
          </div>
        </div>

        <div className="card">
          <div className="kpi-title">Gross Operating Margin</div>
          <div className="kpi-value">66.08%</div>
          <div className="kpi-delta positive">
            <span>✓ Constant</span>
            <span style={{ color: "var(--text-muted)", marginLeft: "4px" }}>within target</span>
          </div>
        </div>

        <div className="card">
          <div className="kpi-title">Avg Order Value (AOV)</div>
          <div className="kpi-value">$268.42</div>
          <div className="kpi-delta positive">
            <span>↑ +2.1%</span>
            <span style={{ color: "var(--text-muted)", marginLeft: "4px" }}>per recognized order</span>
          </div>
        </div>

        <div className="card">
          <div className="kpi-title">Anomaly Alert</div>
          <div className="kpi-value" style={{ color: "var(--accent-rose)", fontSize: "22px" }}>North Missed</div>
          <div className="kpi-delta negative">
            <span>-20.77%</span>
            <span style={{ color: "var(--text-muted)", marginLeft: "4px" }}>off March target</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Regional Performance & Target vs Actual */}
      <div className="grid-2" style={{ marginBottom: "28px" }}>
        {/* Regional Breakdown Card */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Regional Performance Divergence</h3>
            <span className="badge badge-amber">Q1 Divergence</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                <span style={{ fontWeight: 600 }}>North (Core Region)</span>
                <span style={{ color: "var(--accent-rose)", fontWeight: 700 }}>$346,000 (-17.60% Q1 Trend)</span>
              </div>
              <div style={{ height: "8px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "54%", height: "100%", background: "linear-gradient(90deg, #f43f5e, #fb7185)" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                <span style={{ fontWeight: 600 }}>South (Growth Segment)</span>
                <span style={{ color: "var(--accent-emerald)", fontWeight: 700 }}>$295,000 (+6.32% Q1 Trend)</span>
              </div>
              <div style={{ height: "8px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "46%", height: "100%", background: "linear-gradient(90deg, #10b981, #34d399)" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                <span style={{ fontWeight: 600 }}>East (Hardware Pilot)</span>
                <span style={{ color: "var(--accent-blue)", fontWeight: 700 }}>$265,000 (Steady)</span>
              </div>
              <div style={{ height: "8px", background: "rgba(255,255,255,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                <div style={{ width: "41%", height: "100%", background: "linear-gradient(90deg, #3b82f6, #60a5fa)" }} />
              </div>
            </div>
          </div>

          <div style={{ marginTop: "20px", padding: "12px", background: "rgba(244, 63, 94, 0.08)", borderRadius: "8px", border: "1px solid rgba(244, 63, 94, 0.2)" }}>
            <p style={{ fontSize: "12px", color: "#fda4af" }}>
              ⚠️ <strong>Key Observation:</strong> North region revenue drop began in February and accelerated in March. Coincides with a 28% reduction in Search Ad spend.
            </p>
          </div>
        </div>

        {/* Target vs Actuals Card */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>March Target vs Actuals</h3>
            <span className="badge badge-blue">March 2026</span>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Target</th>
                  <th>Actual</th>
                  <th>Achievement</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>North</strong></td>
                  <td>$130,000</td>
                  <td style={{ color: "var(--accent-rose)", fontWeight: 700 }}>$103,000</td>
                  <td><span className="badge badge-rose">79.23% (-$27k)</span></td>
                </tr>
                <tr>
                  <td><strong>South</strong></td>
                  <td>$100,000</td>
                  <td style={{ color: "var(--accent-emerald)", fontWeight: 700 }}>$101,000</td>
                  <td><span className="badge badge-emerald">101.00% (Met)</span></td>
                </tr>
                <tr>
                  <td><strong>Total</strong></td>
                  <td>$230,000</td>
                  <td>$204,000</td>
                  <td><span className="badge badge-amber">88.70%</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: "16px", display: "flex", gap: "10px" }}>
            <button
              className="btn btn-secondary"
              style={{ fontSize: "12px", padding: "6px 12px" }}
              onClick={() => onNavigate("investigation", "Audit marketing spend and regional target divergence")}
            >
              Investigate Target Miss
            </button>
            <button
              className="btn btn-secondary"
              style={{ fontSize: "12px", padding: "6px 12px" }}
              onClick={() => onNavigate("knowledge")}
            >
              View Q1 Financial Memos
            </button>
          </div>
        </div>
      </div>

      {/* Live Read-Only SQL Analytics Console */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
          <div>
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>AST-Protected Read-Only SQL Console</h3>
            <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              Directly executes validated SELECT queries against approved schema tables with row limits and timeout protection.
            </p>
          </div>
          <span className="badge badge-emerald">AST SQL Validator Active</span>
        </div>

        <div style={{ display: "flex", gap: "10px", marginBottom: "12px" }}>
          <input
            className="input"
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            style={{ fontFamily: "var(--font-mono)", fontSize: "13px" }}
          />
          <button className="btn btn-primary" onClick={runQuery} disabled={sqlLoading}>
            {sqlLoading ? "Executing…" : "Execute"}
          </button>
        </div>

        {sqlError && <div style={{ color: "var(--accent-rose)", fontSize: "13px", marginBottom: "10px" }}>{sqlError}</div>}

        {sqlResult.length > 0 && (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(sqlResult[0]).map((k) => (
                    <th key={k}>{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sqlResult.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((v, cIdx) => (
                      <td key={cIdx}>{String(v)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
