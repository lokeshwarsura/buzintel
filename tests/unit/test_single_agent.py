from backend.agents.single_agent import run_single_agent
from backend.models import InvestigationRequest


def test_langgraph_single_agent_returns_structured_report() -> None:
    report = run_single_agent(InvestigationRequest(question="Compare revenue"), "demo")
    assert report.status == "complete"
    assert report.execution_mode == "single"
