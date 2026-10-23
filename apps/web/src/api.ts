/**
 * Typed API client for BizIntel AI backend.
 */

export interface Evidence {
  evidence_id: string;
  source_type: "metric" | "document";
  title: string;
  excerpt: string;
  source_ref: string;
  workspace_id: string;
}

export interface Finding {
  statement: string;
  status: "confirmed" | "hypothesis" | "insufficient_evidence";
  evidence_ids: string[];
}

export interface Recommendation {
  priority: number;
  action: string;
  rationale: string;
  evidence_ids: string[];
}

export interface InvestigationReport {
  investigation_id: string;
  question: string;
  execution_mode: "single" | "multi";
  status: "complete" | "needs_clarification" | "insufficient_evidence";
  executive_summary: string;
  reporting_period?: string;
  findings: Finding[];
  recommendations: Recommendation[];
  limitations: string[];
  citations: Evidence[];
  trace_id: string;
  created_at: string;
}

export interface AgentRunResponse {
  run_id: string;
  investigation_id: string;
  agent_role: string;
  status: string;
  step_number: number;
  details?: string;
  duration_ms: number;
  started_at: string;
}

export interface EvaluationRunResponse {
  run_id: string;
  workspace_id: string;
  suite_name: string;
  execution_mode: string;
  status: string;
  total_cases: number;
  passed_cases: number;
  precision_at_k: number;
  recall_at_k: number;
  citation_validity: number;
  latency_ms: number;
  cost_estimate: number;
  results: Record<string, unknown>;
  created_at: string;
}

export interface DocumentResponse {
  document_id: string;
  workspace_id: string;
  name: string;
  content_hash: string;
  byte_size: number;
  status: string;
  created_at: string;
}

export interface DocumentChunkResponse {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  source_location: string;
  text: string;
  created_at: string;
}

export interface DatasetResponse {
  dataset_id: string;
  workspace_id: string;
  name: string;
  description?: string;
  source_type: string;
  row_count: number;
  schema_json?: string;
  created_at: string;
}

export interface WorkspaceResponse {
  workspace_id: string;
  name: string;
  role: string;
  created_at: string;
}

export interface TraceData {
  trace_id: string;
  root_span: {
    name: string;
    investigation_id: string;
    status: string;
    created_at: string;
  };
  spans: Array<{
    span_id: string;
    name: string;
    status: string;
    start_time: string;
    duration_ms: number;
    attributes: Record<string, unknown>;
  }>;
}

const API_BASE = "";

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchReadiness(): Promise<{ status: string; database: string }> {
  const res = await fetch(`${API_BASE}/ready`);
  return res.json();
}

export async function createInvestigation(
  workspaceId: string,
  question: string,
  mode: "single" | "multi" = "multi",
  reportingPeriod?: string
): Promise<InvestigationReport> {
  const res = await fetch(`${API_BASE}/api/v1/investigations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-ID": workspaceId,
    },
    body: JSON.stringify({ question, mode, reporting_period: reportingPeriod }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Investigation failed" }));
    throw new Error(err.detail || "Investigation failed");
  }
  return res.json();
}

export async function fetchInvestigations(
  workspaceId: string
): Promise<Array<{ investigation_id: string; question: string; execution_mode: string; status: string; executive_summary: string; created_at: string }>> {
  const res = await fetch(`${API_BASE}/api/v1/investigations`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function fetchInvestigationTimeline(
  workspaceId: string,
  investigationId: string
): Promise<AgentRunResponse[]> {
  const res = await fetch(`${API_BASE}/api/v1/investigations/${investigationId}/timeline`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function fetchInvestigationTraces(
  workspaceId: string,
  investigationId: string
): Promise<TraceData> {
  const res = await fetch(`${API_BASE}/api/v1/investigations/${investigationId}/traces`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function fetchDocuments(workspaceId: string): Promise<DocumentResponse[]> {
  const res = await fetch(`${API_BASE}/api/v1/documents`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function fetchDocumentChunks(
  workspaceId: string,
  documentId: string
): Promise<DocumentChunkResponse[]> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${documentId}/chunks`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function uploadDocument(
  workspaceId: string,
  file: File
): Promise<DocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/documents`, {
    method: "POST",
    headers: { "X-Workspace-ID": workspaceId },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function runBenchmark(
  workspaceId: string,
  suiteName = "business_analytics_benchmark_v1",
  executionMode = "comparison"
): Promise<EvaluationRunResponse> {
  const res = await fetch(`${API_BASE}/api/v1/evaluations/benchmark`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-ID": workspaceId,
    },
    body: JSON.stringify({ suite_name: suiteName, execution_mode: executionMode }),
  });
  if (!res.ok) throw new Error("Benchmark run failed");
  return res.json();
}

export async function fetchEvaluationRuns(workspaceId: string): Promise<EvaluationRunResponse[]> {
  const res = await fetch(`${API_BASE}/api/v1/evaluations/runs`, {
    headers: { "X-Workspace-ID": workspaceId },
  });
  return res.json();
}

export async function queryDataset(
  workspaceId: string,
  datasetId: string,
  query: string
): Promise<{ rows: Array<Record<string, unknown>>; count: number; status: string }> {
  const res = await fetch(`${API_BASE}/api/v1/datasets/${datasetId}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-ID": workspaceId,
    },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Query rejected" }));
    throw new Error(err.detail || "Query rejected");
  }
  return res.json();
}
