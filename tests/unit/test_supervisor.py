from backend.agents.supervisor import TASKS, run_supervisor
from backend.models import InvestigationRequest


def test_supervisor_has_bounded_specialists_and_report() -> None:
    report = run_supervisor(InvestigationRequest(question="Investigate revenue"), "demo")
    assert len(TASKS) == 3 and report.execution_mode == "multi" and report.citations
