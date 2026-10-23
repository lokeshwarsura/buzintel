from backend.agents.workflow import run_investigation
from backend.models import InvestigationRequest


def test_investigation_reports_observations_without_causal_claim() -> None:
    report = run_investigation(InvestigationRequest(question="Why did revenue decline?"), "alpha")
    assert report.status == "complete"
    assert report.citations
    assert "does not claim a cause" in report.executive_summary
