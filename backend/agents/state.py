"""Typed state for both execution modes."""

from dataclasses import dataclass, field

from backend.models import Evidence


@dataclass
class InvestigationState:
    investigation_id: str
    trace_id: str
    workspace_id: str
    question: str
    mode: str
    reporting_period: str | None
    evidence: list[Evidence] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    max_tool_calls: int = 4

    def record_tool(self, name: str) -> None:
        if len(self.tool_calls) >= self.max_tool_calls:
            raise RuntimeError("Tool-call limit reached.")
        self.tool_calls.append(name)
