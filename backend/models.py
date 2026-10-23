"""Shared domain contracts and API request/response models."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    evidence_id: str
    source_type: Literal["metric", "document"]
    title: str
    excerpt: str
    source_ref: str
    workspace_id: str


class Finding(BaseModel):
    statement: str
    status: Literal["confirmed", "hypothesis", "insufficient_evidence"]
    evidence_ids: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    priority: int = Field(ge=1, le=3)
    action: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)


class InvestigationReport(BaseModel):
    investigation_id: str
    question: str
    execution_mode: Literal["single", "multi"]
    status: Literal["complete", "needs_clarification", "insufficient_evidence"]
    executive_summary: str
    reporting_period: str | None = None
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    citations: list[Evidence] = Field(default_factory=list)
    trace_id: str
    created_at: datetime


class InvestigationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    mode: Literal["single", "multi"] = "single"
    reporting_period: str | None = Field(default=None, max_length=64)


class Credentials(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12, max_length=256)


class UserResponse(BaseModel):
    user_id: str
    email: str
    created_at: datetime


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    role: str = "member"
    created_at: datetime


class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    source_type: str = "csv"


class DatasetResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    dataset_id: str
    workspace_id: str
    name: str
    description: str | None = None
    source_type: str
    row_count: int
    schema_def: str | None = Field(default=None, serialization_alias="schema_json")
    created_at: datetime


class DatasetQueryRequest(BaseModel):
    query: str = Field(min_length=5, max_length=2000)


class ConversationCreate(BaseModel):
    title: str = Field(default="New Business Investigation", max_length=255)


class ConversationResponse(BaseModel):
    conversation_id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    sender_role: str
    content: str
    created_at: datetime


class DocumentResponse(BaseModel):
    document_id: str
    workspace_id: str
    name: str
    content_hash: str
    byte_size: int
    status: str
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    source_location: str
    text: str
    created_at: datetime


class AgentRunResponse(BaseModel):
    run_id: str
    investigation_id: str
    agent_role: str
    status: str
    step_number: int
    details: str | None = None
    duration_ms: int
    started_at: datetime


class ToolCallResponse(BaseModel):
    call_id: str
    investigation_id: str
    tool_name: str
    tool_args: dict[str, Any] = Field(default_factory=dict)
    tool_result: dict[str, Any] = Field(default_factory=dict)
    is_error: bool
    duration_ms: int
    created_at: datetime


class EvaluationRunCreate(BaseModel):
    suite_name: str = Field(default="business_analytics_benchmark_v1", max_length=100)
    execution_mode: Literal["rag", "single", "multi", "comparison"] = "comparison"


class EvaluationRunResponse(BaseModel):
    run_id: str
    workspace_id: str
    suite_name: str
    execution_mode: str
    status: str
    total_cases: int
    passed_cases: int
    precision_at_k: float
    recall_at_k: float
    citation_validity: float
    latency_ms: int
    cost_estimate: float
    results: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditEventResponse(BaseModel):
    event_id: str
    workspace_id: str
    action: str
    resource_type: str
    resource_id: str | None = None
    details: str | None = None
    created_at: datetime
