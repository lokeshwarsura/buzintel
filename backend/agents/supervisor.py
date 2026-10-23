"""Bounded hierarchical fallback sharing the approved metric and document tools."""

from dataclasses import dataclass

from backend.agents.workflow import run_investigation
from backend.models import InvestigationReport, InvestigationRequest


@dataclass(frozen=True)
class SpecialistTask:
    name: str
    purpose: str


TASKS = (SpecialistTask("metric_analyst", "Compute defined KPIs."), SpecialistTask("document_researcher", "Retrieve authorized evidence."), SpecialistTask("evidence_validator", "Check citations and limitations."))


def run_supervisor(request: InvestigationRequest, workspace_id: str) -> InvestigationReport:
    if request.mode != "multi":
        request = request.model_copy(update={"mode": "multi"})
    return run_investigation(request, workspace_id)
