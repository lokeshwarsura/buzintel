"""LangGraph-backed bounded single-agent workflow using controlled tools only."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from backend.analytics.execution import metric_evidence
from backend.ingestion.service import document_store
from backend.models import Evidence, InvestigationRequest, InvestigationReport


class SingleAgentState(TypedDict, total=False):
    request: InvestigationRequest
    workspace_id: str
    evidence: list[Evidence]
    tool_calls: int
    report: InvestigationReport


def collect_metrics(state: SingleAgentState) -> SingleAgentState:
    return {"evidence": metric_evidence(state["workspace_id"]), "tool_calls": 1}


def collect_documents(state: SingleAgentState) -> SingleAgentState:
    request = state["request"]
    evidence = [*state["evidence"], *document_store.search(state["workspace_id"], request.question)]
    return {"evidence": evidence, "tool_calls": state["tool_calls"] + 1}


def synthesize(state: SingleAgentState) -> SingleAgentState:
    # Reuse the shared report implementation: both modes share metrics/retrieval controls.
    from backend.agents.workflow import run_investigation

    return {"report": run_investigation(state["request"], state["workspace_id"])}


def build_single_agent_graph():
    graph = StateGraph(SingleAgentState)
    graph.add_node("collect_metrics", collect_metrics)
    graph.add_node("collect_documents", collect_documents)
    graph.add_node("synthesize", synthesize)
    graph.add_edge(START, "collect_metrics")
    graph.add_edge("collect_metrics", "collect_documents")
    graph.add_edge("collect_documents", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


def run_single_agent(request: InvestigationRequest, workspace_id: str) -> InvestigationReport:
    result = build_single_agent_graph().invoke({"request": request, "workspace_id": workspace_id})
    return result["report"]
