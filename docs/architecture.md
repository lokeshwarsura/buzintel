# BizIntel AI Architecture

BizIntel AI is an agentic business analytics and decision intelligence platform built as a clean, modular system with clear separation between user interface, REST APIs, multi-agent orchestration, deterministic semantic calculations, persistent storage, and observability.

## High-Level Architecture Diagram

```mermaid
graph TD
    Client[React + Vite Frontend (apps/web)] -->|REST / JSON| API[FastAPI Layer (apps/api)]
    
    subgraph Security & Isolation
        API --> Auth[scrypt Password & Session Tokens]
        API --> Workspace[Workspace Authorization Guard]
    end

    subgraph Agentic Orchestration Layer
        API --> Supervisor[Supervisor / Planner Agent]
        Supervisor --> MetricAnalyst[Metric Analyst]
        Supervisor --> DocResearcher[Document Researcher]
        Supervisor --> TrendAnalyst[Trend & Anomaly Analyst]
        Supervisor --> EvidenceCritic[Evidence Validator / Critic]
        Supervisor --> ReportSynth[Report Synthesizer]
    end

    subgraph Data & Tool Layer
        MetricAnalyst --> Semantics[Canonical KPI Engine]
        DocResearcher --> HybridRAG[Hybrid Lexical + Vector Retrieval]
        TrendAnalyst --> SeedData[Synthetic Relational Data Layer]
        API --> ASTValidator[Tokenizing AST SQL Validator]
        ASTValidator --> SafeSQL[Read-Only Parameterized DB Engine]
    end

    subgraph Persistence Layer
        API --> DB[(SQLite / PostgreSQL + pgvector)]
        Supervisor --> DB
        HybridRAG --> DB
        DB --- Models[15 SQLAlchemy ORM Tables]
    end

    subgraph Observability
        Supervisor --> Trace[OpenTelemetry Span Hierarchy]
        Supervisor --> Audit[Workspace Audit Event Ledger]
    end
```

## Core Subsystems

### 1. Multi-Agent Orchestration (`backend/agents/`)
- **Supervisor / Planner**: Decomposes user questions into bounded sub-tasks and delegates to specialists.
- **Metric Analyst**: Calculates canonical business KPIs (Revenue, Gross Margin, Gross Profit, Target Achievement, AOV) using verified arithmetic.
- **Document Researcher**: Conducts hybrid search across workspace documents with source provenance.
- **Trend & Anomaly Analyst**: Evaluates chronological variance using z-scores and detects correlation with marketing shifts.
- **Evidence Validator / Critic**: Validates citation integrity, checks for conflicting evidence, flags unproven assertions, and enforces separation of confirmed observations from hypotheses.
- **Report Synthesizer**: Formulates the final `InvestigationReport` with executive summary, prioritized recommendations, limitations, and citations.

### 2. Hybrid RAG & Ingestion (`backend/ingestion/`)
- Multi-format text extraction for PDF, DOCX, TXT, MD, CSV, and XLSX.
- SHA-256 content deduplication and workspace isolation.
- Stable chunk identifiers (`doc:{uuid}:{chunk_index}`) and source location markers (`page:1`, `sheet:Sales`).
- 64-dimensional semantic n-gram vector embeddings with L2 normalization.
- Hybrid fusion scoring: `0.5 * normalized_lexical + 0.5 * cosine_similarity`.
- Prompt-injection defense: Sanitizes untrusted document text of override tokens (`ignore previous instructions`, `system:`, etc.).

### 3. Analytics & AST SQL Safety (`backend/analytics/`)
- Mathematical KPI library with explicit non-zero baseline checks.
- Tokenizing recursive-descent AST parser for SQL validation:
  - Enforces single-statement `SELECT` or `WITH`.
  - Rejects comments, semicolons, and stacked queries.
  - Rejects mutation keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`).
  - Enforces strict table allowlists (`orders`, `sales`, `targets`, `marketing_spend`).
  - Enforces row limits (`LIMIT 500`) and query timeouts.

### 4. Persistence & Database Migrations (`backend/db/`, `alembic/`)
- 15 relational tables managed via SQLAlchemy 2.0 ORM:
  - Identity: `users`, `workspaces`, `workspace_members`, `auth_sessions`
  - Catalog: `datasets`, `documents`, `document_chunks`
  - Collaboration: `conversations`, `messages`
  - Intelligence: `investigations`, `agent_runs`, `investigation_evidence`, `tool_calls`
  - Governance: `audit_events`, `evaluation_runs`
- Versioned Alembic migrations supporting SQLite for local development and PostgreSQL + pgvector for production deployment.

### 5. Observability & Traces (`apps/api/`)
- OpenTelemetry-compatible trace hierarchies generated for every investigation:
  - Root span: `investigation.{single|multi}`
  - Child spans: `agent.{role}` and `tool.{name}`
  - Recorded attributes: timestamps, latencies (ms), step count, and redacted arguments.
- Complete audit logging on workspace operations.

### 6. User Interface (`apps/web/`)
- 5 comprehensive pages built with React, Vite, and TypeScript:
  - Executive Dashboard
  - AI Investigation Workspace
  - Knowledge Base
  - Agent Trace Viewer
  - Evaluation Laboratory
