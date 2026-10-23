"""Persistent identity and workspace authorization operations."""

import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.db.models import AuthSession, User, Workspace, WorkspaceMember


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


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
    return workspace


def list_workspaces(session: Session, user: User) -> list[Workspace]:
    return list(session.scalars(select(Workspace).join(WorkspaceMember).where(WorkspaceMember.user_id == user.id)))


def require_membership(session: Session, user: User, workspace_id: str) -> Workspace:
    workspace = session.scalar(select(Workspace).join(WorkspaceMember).where(Workspace.id == workspace_id, WorkspaceMember.user_id == user.id))
    if not workspace:
        raise PermissionError("You do not have access to this workspace.")
    return workspace
