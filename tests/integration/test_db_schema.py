from sqlalchemy import select

from backend.db.models import User, Workspace, WorkspaceMember
from backend.db.session import Base, build_session_factory


def test_sqlite_development_schema_enforces_workspace_membership(tmp_path) -> None:
    factory, engine = build_session_factory(f"sqlite:///{tmp_path / 'bizintel.db'}")
    Base.metadata.create_all(engine)
    with factory.begin() as session:
        user = User(email="demo@example.test", password_hash="scrypt$test$test")
        session.add(user)
        session.flush()
        workspace = Workspace(name="Demo", owner_id=user.id)
        session.add(workspace)
        session.flush()
        session.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner"))
    with factory() as session:
        assert session.scalar(select(WorkspaceMember).where(WorkspaceMember.role == "owner"))
