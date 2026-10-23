"""A deterministic, bounded initial investigation workflow.

The graph adapter is intentionally deferred until LangGraph is installed; these nodes
are directly testable and will become LangGraph nodes without duplicating logic.
"""

from datetime import UTC, datetime
from uuid import uuid4

from backend.analytics.execution import metric_evidence
from backend.ingestion.service import document_store
from backend.models import Finding, InvestigationReport, InvestigationRequest, Recommendation


def run_investigation(request: InvestigationRequest, workspace_id: str) -> InvestigationReport:
    investigation_id, trace_id = str(uuid4()), str(uuid4())
    evidence = metric_evidence(workspace_id)
    document_evidence = document_store.search(workspace_id, request.question)
    if request.mode == "multi":
        # Supervisor combines only outputs from the same controlled tool layer.
        evidence.extend(document_evidence)
    else:
        evidence.extend(document_evidence[:3])
    growth = next(item for item in evidence if item.evidence_id == "metric:growth:jan-mar")
    margin = next(item for item in evidence if item.evidence_id == "metric:margin:2026-q1")
    findings = [
        Finding(statement=growth.excerpt, status="confirmed", evidence_ids=[growth.evidence_id]),
        Finding(statement=margin.excerpt, status="confirmed", evidence_ids=[margin.evidence_id]),
    ]
    if document_evidence:
        findings.append(
            Finding(
                statement="Relevant authorized document passages were retrieved; they are supporting context, not proof of causation.",
                status="confirmed",
                evidence_ids=[item.evidence_id for item in document_evidence],
            )
        )
    recommendations = [
        Recommendation(
            priority=1,
            action="Review the North-region revenue decline by account and channel.",
            rationale="North revenue decreased in the synthetic monthly data; further segment-level evidence is needed before assigning cause.",
            evidence_ids=[growth.evidence_id],
        ),
        Recommendation(
            priority=2,
            action="Validate pricing, churn, and pipeline data before intervening.",
            rationale="The available dataset supports a trend but does not establish causation.",
            evidence_ids=[growth.evidence_id],
        ),
        Recommendation(
            priority=3,
            action="Monitor gross-margin movement alongside revenue recovery actions.",
            rationale="Protecting margin is a defined KPI constraint.",
            evidence_ids=[margin.evidence_id],
        ),
    ]
    return InvestigationReport(
        investigation_id=investigation_id,
        trace_id=trace_id,
        question=request.question,
        execution_mode=request.mode,
        status="complete",
        executive_summary="The synthetic data shows a January-to-March revenue decline. The system reports the observed trend but does not claim a cause without supporting evidence.",
        reporting_period=request.reporting_period or "2026-01 to 2026-03",
        findings=findings,
        recommendations=recommendations,
        limitations=[
            "This local mode uses a small synthetic dataset.",
            "Retrieved documents are treated as untrusted evidence.",
            "No causal claim is made from trend data alone.",
        ],
        citations=evidence,
        created_at=datetime.now(UTC),
    )
