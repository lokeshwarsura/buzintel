"""Persistent identity, workspace authorization, and domain entity operations."""

import hashlib
import json
import secrets
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.db.models import (
    AgentRunRecord,
    AuditEventRecord,
    AuthSession,
    Conversation,
    DatasetRecord,
    DocumentChunkRecord,
    EvaluationRunRecord,
    InvestigationEvidenceRecord,
    InvestigationRecord,
    Message,
    StoredDocumentRecord,
    ToolCallRecord,
    User,
    Workspace,
    WorkspaceMember,
)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# Auth & Workspace


def register_user(session: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    if session.scalar(select(User).where(User.email == email)):
        raise ValueError("Email is already registered.")
    user = User(email=email, password_hash=hash_password(password))
    session.add(user)
    session.flush()
    return user


def login_user(session: Session, email: str, password: str) -> str:
    user = session.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        raise PermissionError("Invalid email or password.")
    token = secrets.token_urlsafe(32)
    session.add(AuthSession(user_id=user.id, token_hash=_token_hash(token)))
    session.flush()
    return token


def current_user(session: Session, token: str) -> User:
    auth = session.scalar(select(AuthSession).where(AuthSession.token_hash == _token_hash(token)))
    if not auth:
        raise PermissionError("Invalid or expired session token.")
    return session.get(User, auth.user_id)


def create_workspace(session: Session, user: User, name: str) -> Workspace:
    workspace = Workspace(name=name.strip(), owner_id=user.id)
    session.add(workspace)
    session.flush()
    session.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner"))
    session.flush()
    return workspace


def list_workspaces(session: Session, user: User) -> list[tuple[Workspace, str]]:
    stmt = (
        select(Workspace, WorkspaceMember.role)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == user.id)
    )
    return list(session.execute(stmt).all())


def require_membership(session: Session, user: User, workspace_id: str) -> Workspace:
    workspace = session.scalar(
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(Workspace.id == workspace_id, WorkspaceMember.user_id == user.id)
    )
    if not workspace:
        raise PermissionError("You do not have access to this workspace.")
    return workspace


# Datasets


def register_dataset(
    session: Session,
    workspace_id: str,
    name: str,
    description: str | None = None,
    source_type: str = "csv",
    row_count: int = 0,
    schema_json: str | None = None,
) -> DatasetRecord:
    dataset = DatasetRecord(
        workspace_id=workspace_id,
        name=name.strip(),
        description=description,
        source_type=source_type,
        row_count=row_count,
        schema_json=schema_json,
    )
    session.add(dataset)
    session.flush()
    return dataset


def list_datasets(session: Session, workspace_id: str) -> list[DatasetRecord]:
    return list(session.scalars(select(DatasetRecord).where(DatasetRecord.workspace_id == workspace_id)))


def get_dataset(session: Session, workspace_id: str, dataset_id: str) -> DatasetRecord | None:
    return session.scalar(
        select(DatasetRecord).where(
            DatasetRecord.workspace_id == workspace_id,
            DatasetRecord.id == dataset_id,
        )
    )


# Documents & Chunks


def list_stored_documents(session: Session, workspace_id: str) -> list[StoredDocumentRecord]:
    return list(session.scalars(select(StoredDocumentRecord).where(StoredDocumentRecord.workspace_id == workspace_id)))


def get_stored_document(session: Session, workspace_id: str, document_id: str) -> StoredDocumentRecord | None:
    return session.scalar(
        select(StoredDocumentRecord).where(
            StoredDocumentRecord.workspace_id == workspace_id,
            StoredDocumentRecord.id == document_id,
        )
    )


def list_document_chunks(session: Session, workspace_id: str, document_id: str) -> list[DocumentChunkRecord]:
    return list(
        session.scalars(
            select(DocumentChunkRecord)
            .where(
                DocumentChunkRecord.document_id == document_id,
                DocumentChunkRecord.workspace_id == workspace_id,
            )
            .order_by(DocumentChunkRecord.chunk_index)
        )
    )


# Conversations & Chat Messages


def create_conversation(session: Session, workspace_id: str, user_id: str, title: str) -> Conversation:
    conversation = Conversation(
        workspace_id=workspace_id,
        user_id=user_id,
        title=title.strip(),
    )
    session.add(conversation)
    session.flush()
    return conversation


def list_conversations(session: Session, workspace_id: str, user_id: str) -> list[Conversation]:
    return list(
        session.scalars(
            select(Conversation)
            .where(Conversation.workspace_id == workspace_id, Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
    )


def get_conversation(session: Session, workspace_id: str, conversation_id: str) -> Conversation | None:
    return session.scalar(
        select(Conversation).where(
            Conversation.workspace_id == workspace_id,
            Conversation.id == conversation_id,
        )
    )


def add_message(
    session: Session,
    conversation_id: str,
    workspace_id: str,
    sender_role: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        sender_role=sender_role,
        content=content.strip(),
    )
    session.add(message)
    session.flush()
    return message


def list_messages(session: Session, conversation_id: str, workspace_id: str) -> list[Message]:
    return list(
        session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.workspace_id == workspace_id)
            .order_by(Message.created_at)
        )
    )


# Investigations & Observability Traces


def list_investigations(session: Session, workspace_id: str, limit: int = 50) -> list[InvestigationRecord]:
    return list(
        session.scalars(
            select(InvestigationRecord)
            .where(InvestigationRecord.workspace_id == workspace_id)
            .order_by(InvestigationRecord.created_at.desc())
            .limit(limit)
        )
    )


def get_investigation(session: Session, workspace_id: str, investigation_id: str) -> InvestigationRecord | None:
    return session.scalar(
        select(InvestigationRecord).where(
            InvestigationRecord.workspace_id == workspace_id,
            InvestigationRecord.id == investigation_id,
        )
    )


def get_investigation_timeline(session: Session, workspace_id: str, investigation_id: str) -> list[AgentRunRecord]:
    return list(
        session.scalars(
            select(AgentRunRecord)
            .where(
                AgentRunRecord.workspace_id == workspace_id,
                AgentRunRecord.investigation_id == investigation_id,
            )
            .order_by(AgentRunRecord.step_number)
        )
    )


def get_investigation_evidence(
    session: Session, workspace_id: str, investigation_id: str
) -> list[InvestigationEvidenceRecord]:
    return list(
        session.scalars(
            select(InvestigationEvidenceRecord)
            .where(
                InvestigationEvidenceRecord.workspace_id == workspace_id,
                InvestigationEvidenceRecord.investigation_id == investigation_id,
            )
        )
    )


def get_investigation_tool_calls(
    session: Session, workspace_id: str, investigation_id: str
) -> list[ToolCallRecord]:
    return list(
        session.scalars(
            select(ToolCallRecord)
            .where(
                ToolCallRecord.workspace_id == workspace_id,
                ToolCallRecord.investigation_id == investigation_id,
            )
            .order_by(ToolCallRecord.created_at)
        )
    )


# Evaluations


def create_evaluation_run(
    session: Session,
    workspace_id: str,
    suite_name: str,
    execution_mode: str,
    status: str = "completed",
    total_cases: int = 0,
    passed_cases: int = 0,
    precision_at_k: float = 0.0,
    recall_at_k: float = 0.0,
    citation_validity: float = 0.0,
    latency_ms: int = 0,
    cost_estimate: float = 0.0,
    results_json: str | None = None,
) -> EvaluationRunRecord:
    run = EvaluationRunRecord(
        workspace_id=workspace_id,
        suite_name=suite_name,
        execution_mode=execution_mode,
        status=status,
        total_cases=total_cases,
        passed_cases=passed_cases,
        precision_at_k=precision_at_k,
        recall_at_k=recall_at_k,
        citation_validity=citation_validity,
        latency_ms=latency_ms,
        cost_estimate=cost_estimate,
        results_json=results_json,
    )
    session.add(run)
    session.flush()
    return run


def list_evaluation_runs(session: Session, workspace_id: str) -> list[EvaluationRunRecord]:
    return list(
        session.scalars(
            select(EvaluationRunRecord)
            .where(EvaluationRunRecord.workspace_id == workspace_id)
            .order_by(EvaluationRunRecord.created_at.desc())
        )
    )


def get_evaluation_run(session: Session, workspace_id: str, run_id: str) -> EvaluationRunRecord | None:
    return session.scalar(
        select(EvaluationRunRecord).where(
            EvaluationRunRecord.workspace_id == workspace_id,
            EvaluationRunRecord.id == run_id,
        )
    )


# Audit Logging


def record_audit_event(
    session: Session,
    workspace_id: str,
    action: str,
    resource_type: str,
    user_id: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditEventRecord:
    event = AuditEventRecord(
        workspace_id=workspace_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details or {}),
        ip_address=ip_address,
    )
    session.add(event)
    session.flush()
    return event


def list_audit_events(session: Session, workspace_id: str, limit: int = 100) -> list[AuditEventRecord]:
    return list(
        session.scalars(
            select(AuditEventRecord)
            .where(AuditEventRecord.workspace_id == workspace_id)
            .order_by(AuditEventRecord.created_at.desc())
            .limit(limit)
        )
    )
