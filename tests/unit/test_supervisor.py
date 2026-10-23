from backend.agents.supervisor import TASKS, run_supervisor
from backend.models import InvestigationRequest


def test_supervisor_has_bounded_specialists_and_report() -> None:
    report = run_supervisor(InvestigationRequest(question="Investigate Q1 revenue decline in North region"), "demo")
    assert len(TASKS) == 6
    assert report.execution_mode == "multi"
    assert report.status == "complete"
    assert len(report.citations) >= 3
    assert len(report.findings) >= 3
    assert len(report.recommendations) == 3

    # Ensure findings distinguish confirmed facts from hypotheses
    statuses = {f.status for f in report.findings}
    assert "confirmed" in statuses
    assert "hypothesis" in statuses
