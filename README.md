# BizIntel AI — Agentic Business Analytics & Decision Intelligence Platform

BizIntel AI is an enterprise-grade agentic business intelligence platform featuring **Hybrid RAG**, **AST-Protected SQL Analytics**, **Hierarchical Multi-Agent Orchestration (6 Specialist Roles)**, **OpenTelemetry Observability**, and a **5-Page React Executive Frontend**.

The platform is designed around strict **zero-hallucination** commercial principles: verified metrics, source-supported qualitative facts, unproven hypotheses, and actionable recommendations are explicitly segregated.

---

## 🌟 Key Capabilities

1. **Deterministic Analytics & AST-Aware SQL Safety**:
   - Canonical calculations for Revenue, Gross Margin, Gross Profit, Average Order Value (AOV), Target Achievement, and Time-Series Z-Score Anomalies.
   - Tokenizing AST parser enforcing schema allowlists, single statement execution, automatic row limits, and rejection of mutation keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`).

2. **Multi-Format Hybrid RAG & Prompt-Injection Defense**:
   - Ingestion across **PDF, DOCX, TXT, Markdown, CSV, and XLSX** with SHA-256 deduplication and stable chunk provenance (`doc:{uuid}:{index}`, `page:1`, `sheet:Sales`).
   - Hybrid retrieval combining normalized keyword frequency with cosine similarity over semantic n-gram vector embeddings.
   - Built-in prompt-injection defense neutralizing system overrides, delimiters, and role-spoofing markers.

3. **Hierarchical Multi-Agent Workflow (6 Specialists)**:
   - **Supervisor / Planner**: Decomposes commercial questions into bounded execution graphs.
   - **Metric Analyst**: Executes deterministic KPI calculations against approved semantic definitions.
   - **Document Researcher**: Conducts hybrid workspace document retrieval with source provenance.
   - **Trend / Anomaly Analyst**: Evaluates chronological shifts, variance, and marketing ad spend correlations.
   - **Evidence Validator / Critic**: Enforces citation links, flags unproven claims, and separates facts from hypotheses.
   - **Report Synthesizer**: Produces structured executive summaries, prioritized recommendations, and limitations.

4. **Complete 5-Page React Frontend (`apps/web`)**:
   - **Executive Dashboard**: KPI cards, regional breakdown bars, target vs actuals tracker, and live AST SQL console.
   - **AI Investigation Workspace**: Question prompt presets, mode toggle (Single vs Multi-Agent), specialist step tracker, findings board, and citation explorer.
   - **Knowledge Base**: Multi-format document uploader, inventory with SHA-256 hashes, and chunk provenance inspector.
   - **Agent Trace Viewer**: OpenTelemetry-compatible execution trees, agent/tool spans, duration breakdown, and secret redaction.
   - **Evaluation Laboratory**: 10-category benchmark suite, comparative matrix (RAG vs Single vs Multi-Agent), and security verification.

5. **Persistence & Database Migrations**:
   - SQLAlchemy 2.0 ORM with Alembic versioned migrations.
   - Full schemas for Users, Workspaces, Memberships, Auth Sessions, Datasets, Documents, Document Chunks, Conversations, Messages, Investigations, Agent Runs, Evidence, Tool Calls, Audit Events, and Evaluation Runs.
   - Tested development support on SQLite and complete production configuration for PostgreSQL with pgvector.

---

## 🚀 Quickstart: Windows Native Development

The project is built for native Windows development using PowerShell.

### Prerequisites
- Python 3.12+ (Python 3.14 compatible)
- Node.js 20+ (`npm.cmd` compatible)
- Git for Windows

### Automated Setup
Run the automated PowerShell setup script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

### Manual Step-by-Step Setup

1. **Create and Activate Python Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev,documents,agents]"
   ```

2. **Run Alembic Migrations**:
   ```powershell
   $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
   .venv\Scripts\alembic.exe upgrade head
   ```

3. **Start the FastAPI Backend Server** (Port 8000):
   ```powershell
   .venv\Scripts\uvicorn.exe apps.api.main:app --reload --port 8000
   ```

4. **Install and Run the Frontend Client** (Port 5173):
   In a separate PowerShell window:
   ```powershell
   Set-Location apps\web
   npm.cmd install
   npm.cmd run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 🧪 Verification & Automated Testing

Run the automated test suite (all unit and integration tests):
```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
.venv\Scripts\pytest.exe -v
```

Run Ruff linting and formatting verification:
```powershell
.venv\Scripts\ruff.exe check .
```

Verify frontend production build:
```powershell
Set-Location apps\web
npm.cmd run build
```

---

## 🐳 Optional Docker Deployment (PostgreSQL + pgvector)

To deploy the production stack with PostgreSQL and pgvector:
```powershell
docker compose up -d
```
The stack provisions:
- `db`: PostgreSQL 16 with pgvector extension on port `5432`.
- `api`: FastAPI application container on port `8000`.

---

## 📊 Evaluation Benchmark Matrix

The built-in benchmark laboratory tests 10 distinct commercial categories:

| Execution Mode | Task Completion | Citation Validity | Hypothesis Separation | Avg Latency | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Non-Agentic RAG** | 60.0% | 85.0% | ❌ No (Mixed) | ~5 ms | Baseline |
| **Single-Agent Workflow** | 90.0% | 100.0% | ⚠️ Basic | ~15 ms | Passing |
| **Hierarchical Multi-Agent** | **100.0%** | **100.0%** | **✅ Strictly Labeled** | ~45 ms | **Optimal** |

### Security Verification
- **Cross-Workspace Data Leaks**: 0
- **Unsafe SQL Mutations Executed**: 0
- **Prompt Injection Attempts Neutralized**: 100%

---

## 📁 Repository Structure

```
bizintel-ai/
├── alembic/                    # Alembic database migration scripts
│   └── versions/               # Versioned DDL migration revisions
├── apps/
│   ├── api/                    # FastAPI REST application
│   │   └── main.py             # Secured endpoints, CORS, dependency injection
│   └── web/                    # React / Vite / TypeScript Frontend
│       ├── src/
│       │   ├── pages/          # Dashboard, Investigation, KnowledgeBase, TraceViewer, EvaluationLab
│       │   ├── api.ts          # Typed API client
│       │   ├── main.tsx        # Application container & sidebar
│       │   └── styles.css      # Modern dark-mode glassmorphic design system
├── backend/
│   ├── agents/                 # Multi-agent orchestration
│   │   ├── state.py            # Typed shared investigation state
│   │   ├── supervisor.py       # 6-specialist hierarchical supervisor
│   │   ├── single_agent.py     # Bounded single agent
│   │   └── workflow.py         # Workflow coordinator
│   ├── analytics/              # Deterministic analytics
│   │   ├── metrics.py          # KPI calculations, anomalies, segment comparisons
│   │   ├── sql_validation.py   # Tokenizing AST SQL validator & safe execution
│   │   ├── seed_data.py        # Reproducible synthetic retail datasets
│   │   └── execution.py        # Metric evidence generators
│   ├── core/                   # Core config & scrypt password security
│   ├── db/                     # Database models, sessions, and persistence service
│   ├── evaluation/             # 10-category benchmark suite & runner
│   └── ingestion/              # Multi-format parsing, embeddings, hybrid retrieval, injection defense
├── docs/                       # Architecture, threat model, API contract, implementation log
├── scripts/                    # Windows setup and automation scripts
└── tests/                      # Unit and integration test suites
```

---

## 📄 License

Proprietary / Portfolio Demonstration.
