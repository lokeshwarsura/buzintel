"""Typed state for single-agent and hierarchical multi-agent execution."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.models import Evidence, Finding, Recommendation


@dataclass
class AgentStepRecord:
    agent_role: str
    action: str
    status: str
    duration_ms: int = 0
    details: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class InvestigationState:
    investigation_id: str
    trace_id: str
    workspace_id: str
    question: str
    mode: str
    reporting_period: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    agent_steps: list[AgentStepRecord] = field(default_factory=list)
    max_tool_calls: int = 10
    max_agent_steps: int = 12

    def record_tool(self, name: str) -> None:
        if len(self.tool_calls) >= self.max_tool_calls:
            raise RuntimeError("Tool-call limit reached.")
        self.tool_calls.append(name)

    def record_step(self, role: str, action: str, status: str = "completed", duration_ms: int = 0, details: str = "") -> None:
        if len(self.agent_steps) >= self.max_agent_steps:
            raise RuntimeError("Agent step execution limit reached.")
        self.agent_steps.append(
            AgentStepRecord(
                agent_role=role,
                action=action,
                status=status,
                duration_ms=duration_ms,
                details=details,
            )
        )
