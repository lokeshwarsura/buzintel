"""Integration test verifying full investigation persistence with specialists, evidence, and tool calls."""

from sqlalchemy import select

from backend.agents.supervisor import run_supervisor
from backend.db.models import (
    AgentRunRecord,
    AuditEventRecord,
    InvestigationEvidenceRecord,
    InvestigationRecord,
    ToolCallRecord,
    User,
    Workspace,
)
from backend.db.session import Base, build_session_factory
from backend.models import InvestigationRequest


def test_investigation_and_specialist_runs_persist_in_db(tmp_path) -> None:
    factory, engine = build_session_factory(f"sqlite:///{tmp_path / 'investigations.db'}")
    Base.metadata.create_all(engine)

    with factory.begin() as session:
        user = User(email="investigator@example.test", password_hash="hash")
        session.add(user)
        session.flush()
        workspace = Workspace(name="Intelligence Lab", owner_id=user.id)
        session.add(workspace)
        session.flush()
        ws_id = workspace.id

    with factory.begin() as session:
        request = InvestigationRequest(
            question="Why did Q1 revenue decline in North region?",
            mode="multi",
            reporting_period="2026-01 to 2026-03",
        )
        report = run_supervisor(request, ws_id, session=session)
        assert report.status == "complete"
        assert report.execution_mode == "multi"

    with factory() as session:
        # 1. Check investigation persisted
        inv = session.scalar(select(InvestigationRecord).where(InvestigationRecord.workspace_id == ws_id))
        assert inv is not None
        assert inv.status == "complete"
        assert "revenue" in inv.executive_summary.lower()

        # 2. Check specialist agent runs persisted
        runs = list(
            session.scalars(
                select(AgentRunRecord)
                .where(AgentRunRecord.investigation_id == inv.id)
                .order_by(AgentRunRecord.step_number)
            )
        )
        assert len(runs) >= 5
        roles = [r.agent_role for r in runs]
        assert "supervisor_planner" in roles
        assert "metric_analyst" in roles
        assert "document_researcher" in roles
        assert "trend_anomaly_analyst" in roles
        assert "evidence_validator" in roles

        # 3. Check evidence persisted
        evidence_items = list(
            session.scalars(
                select(InvestigationEvidenceRecord)
                .where(InvestigationEvidenceRecord.investigation_id == inv.id)
            )
        )
        assert len(evidence_items) >= 4

        # 4. Check tool calls persisted
        tools = list(
            session.scalars(
                select(ToolCallRecord).where(ToolCallRecord.investigation_id == inv.id)
            )
        )
        assert len(tools) >= 3
        tool_names = [t.tool_name for t in tools]
        assert "calculate_kpis" in tool_names
        assert "search_documents" in tool_names

        # 5. Check audit event persisted
        audit = session.scalar(
            select(AuditEventRecord).where(
                AuditEventRecord.workspace_id == ws_id,
                AuditEventRecord.action == "investigation:completed",
            )
        )
        assert audit is not None
        assert audit.resource_id == inv.id
