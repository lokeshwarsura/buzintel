"""initial_schema

Revision ID: 916015f75918
Revises: 
Create Date: 2026-10-23 20:23:39.523609

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '916015f75918'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('owner_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_workspaces_owner_id', 'workspaces', ['owner_id'])

    # 3. workspace_members
    op.create_table(
        'workspace_members',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_member'),
    )
    op.create_index('ix_workspace_members_workspace_id', 'workspace_members', ['workspace_id'])
    op.create_index('ix_workspace_members_user_id', 'workspace_members', ['user_id'])

    # 4. auth_sessions
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_token_hash', 'auth_sessions', ['token_hash'], unique=True)

    # 5. datasets
    op.create_table(
        'datasets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('schema_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_datasets_workspace_id', 'datasets', ['workspace_id'])

    # 6. documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('byte_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_documents_workspace_id', 'documents', ['workspace_id'])
    op.create_index('ix_documents_content_hash', 'documents', ['content_hash'])

    # 7. document_chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(length=80), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('source_location', sa.String(length=100), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])
    op.create_index('ix_document_chunks_workspace_id', 'document_chunks', ['workspace_id'])

    # 8. conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_conversations_workspace_id', 'conversations', ['workspace_id'])
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # 9. messages
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('sender_role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_workspace_id', 'messages', ['workspace_id'])

    # 10. investigations
    op.create_table(
        'investigations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('trace_id', sa.String(length=36), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('execution_mode', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('reporting_period', sa.String(length=64), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('findings_json', sa.Text(), nullable=True),
        sa.Column('recommendations_json', sa.Text(), nullable=True),
        sa.Column('limitations_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_investigations_workspace_id', 'investigations', ['workspace_id'])
    op.create_index('ix_investigations_user_id', 'investigations', ['user_id'])
    op.create_index('ix_investigations_trace_id', 'investigations', ['trace_id'])

    # 11. agent_runs
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('agent_role', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('input_state_json', sa.Text(), nullable=True),
        sa.Column('output_state_json', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_agent_runs_investigation_id', 'agent_runs', ['investigation_id'])
    op.create_index('ix_agent_runs_workspace_id', 'agent_runs', ['workspace_id'])

    # 12. investigation_evidence
    op.create_table(
        'investigation_evidence',
        sa.Column('id', sa.String(length=80), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('evidence_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('source_ref', sa.String(length=255), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_investigation_evidence_investigation_id', 'investigation_evidence', ['investigation_id'])
    op.create_index('ix_investigation_evidence_workspace_id', 'investigation_evidence', ['workspace_id'])

    # 13. tool_calls
    op.create_table(
        'tool_calls',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('investigation_id', sa.String(length=36), sa.ForeignKey('investigations.id'), nullable=False),
        sa.Column('agent_run_id', sa.String(length=36), sa.ForeignKey('agent_runs.id'), nullable=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('tool_args_json', sa.Text(), nullable=False),
        sa.Column('tool_result_json', sa.Text(), nullable=False),
        sa.Column('is_error', sa.Boolean(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tool_calls_investigation_id', 'tool_calls', ['investigation_id'])
    op.create_index('ix_tool_calls_agent_run_id', 'tool_calls', ['agent_run_id'])
    op.create_index('ix_tool_calls_workspace_id', 'tool_calls', ['workspace_id'])
    op.create_index('ix_tool_calls_tool_name', 'tool_calls', ['tool_name'])

    # 14. audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_events_workspace_id', 'audit_events', ['workspace_id'])
    op.create_index('ix_audit_events_user_id', 'audit_events', ['user_id'])
    op.create_index('ix_audit_events_action', 'audit_events', ['action'])

    # 15. evaluation_runs
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('suite_name', sa.String(length=100), nullable=False),
        sa.Column('execution_mode', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_cases', sa.Integer(), nullable=False),
        sa.Column('passed_cases', sa.Integer(), nullable=False),
        sa.Column('precision_at_k', sa.Float(), nullable=False),
        sa.Column('recall_at_k', sa.Float(), nullable=False),
        sa.Column('citation_validity', sa.Float(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('cost_estimate', sa.Float(), nullable=False),
        sa.Column('results_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_evaluation_runs_workspace_id', 'evaluation_runs', ['workspace_id'])


def downgrade() -> None:
    op.drop_table('evaluation_runs')
    op.drop_table('audit_events')
    op.drop_table('tool_calls')
    op.drop_table('investigation_evidence')
    op.drop_table('agent_runs')
    op.drop_table('investigations')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('datasets')
    op.drop_table('auth_sessions')
    op.drop_table('workspace_members')
    op.drop_table('workspaces')
    op.drop_table('users')
