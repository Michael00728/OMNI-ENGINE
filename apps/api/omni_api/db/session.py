"""Database engine, sessions, and fail-closed tenant transaction context."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from sqlalchemy import Engine, create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from omni_api.config import get_settings
from omni_api.db.models import Tenant, TenantMembership, TenantStatus


_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(get_settings().database_url, pool_pre_ping=True, future=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """Yield a session; callers must explicitly establish tenant context for RLS tables."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def tenant_transaction(session: Session, tenant_id: UUID) -> Iterator[Session]:
    """Set transaction-local RLS context; this low-level helper does not authenticate users."""
    if session.in_transaction():
        raise RuntimeError("tenant_transaction requires a session with no active transaction")
    with session.begin():
        session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        yield session


@contextmanager
def authorized_tenant_transaction(
    session: Session, tenant_id: UUID, authenticated_user_id: UUID
) -> Iterator[tuple[Session, str]]:
    """Verify an active tenant and authenticated user's membership before yielding."""
    with tenant_transaction(session, tenant_id) as scoped_session:
        tenant_status = scoped_session.execute(
            select(Tenant.status).where(Tenant.id == tenant_id)
        ).scalar_one_or_none()
        if tenant_status != TenantStatus.ACTIVE.value:
            raise PermissionError("Tenant is not active")

        role = scoped_session.execute(
            select(TenantMembership.role).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == authenticated_user_id,
            )
        ).scalar_one_or_none()
        if role is None:
            raise PermissionError("User is not a member of this tenant")
        yield scoped_session, role


def check_database() -> bool:
    """Check database connectivity without exposing connection details."""
    with get_engine().connect() as connection:
        return connection.execute(text("SELECT 1")).scalar_one() == 1
