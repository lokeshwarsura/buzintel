"""Shared domain contracts used by API, tools, and agent workflows."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
