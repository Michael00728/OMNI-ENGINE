from pathlib import Path
from uuid import uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint

from omni_api.db.base import Base
from omni_api.db.models import AuditEvent, Tenant, TenantMembership

MIGRATION = Path("apps/api/alembic/versions/0001_tenant_security.py")


def test_expected_tenant_tables_are_registered() -> None:
    assert {"tenants", "tenant_memberships", "audit_events"}.issubset(Base.metadata.tables)


def test_membership_is_unique_per_tenant_and_user() -> None:
    constraints = TenantMembership.__table__.constraints
    assert any(
        isinstance(item, UniqueConstraint)
        and {column.name for column in item.columns} == {"tenant_id", "user_id"}
        for item in constraints
    )


def test_role_and_tenant_status_are_constrained() -> None:
    tenant_checks = [item for item in Tenant.__table__.constraints if isinstance(item, CheckConstraint)]
    membership_checks = [item for item in TenantMembership.__table__.constraints if isinstance(item, CheckConstraint)]
    assert any("active" in str(item.sqltext) and "suspended" in str(item.sqltext) for item in tenant_checks)
    assert any("read_only" in str(item.sqltext) for item in membership_checks)


def test_audit_event_has_tenant_and_actor_fields() -> None:
    columns = AuditEvent.__table__.columns
    assert columns.tenant_id.nullable is False
    assert columns.actor_user_id.nullable is True
    assert columns.event_metadata.nullable is False
    assert columns.created_at.nullable is False


def test_tenant_ids_are_uuid_columns() -> None:
    assert Tenant.__table__.c.id.type.python_type is type(uuid4())
    assert TenantMembership.__table__.c.tenant_id.type.python_type is type(uuid4())


def test_migration_enables_forced_rls_and_append_only_audit_access() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    assert "ENABLE ROW LEVEL SECURITY" in migration
    assert "FORCE ROW LEVEL SECURITY" in migration
    assert "current_setting('app.tenant_id', true)" in migration
    assert "GRANT SELECT, INSERT ON audit_events TO omni_app" in migration
    assert "GRANT SELECT, INSERT, UPDATE, DELETE ON audit_events TO omni_app" not in migration
