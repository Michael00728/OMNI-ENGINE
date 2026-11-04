"""PostgreSQL integration tests; skipped unless CI supplies isolated test URLs."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from omni_api.db.session import authorized_tenant_transaction, check_database

ADMIN_URL = os.getenv("OMNI_TEST_ADMIN_DATABASE_URL")
RUNTIME_URL = os.getenv("OMNI_TEST_RUNTIME_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not ADMIN_URL or not RUNTIME_URL,
    reason="PostgreSQL RLS integration URLs are not configured",
)


def test_runtime_role_sees_current_database_schema_revision() -> None:
    assert check_database() is True


def test_runtime_role_is_tenant_isolated_and_audit_is_append_only() -> None:
    admin_engine = create_engine(ADMIN_URL, future=True)
    runtime_engine = create_engine(RUNTIME_URL, future=True)
    tenant_a, tenant_b, tenant_suspended = uuid4(), uuid4(), uuid4()
    user_a, user_b, user_suspended = uuid4(), uuid4(), uuid4()

    try:
        with admin_engine.begin() as connection:
            connection.execute(
                text("INSERT INTO tenants (id, name, status) VALUES (:id, :name, :status)"),
                [
                    {"id": tenant_a, "name": "Tenant A", "status": "active"},
                    {"id": tenant_b, "name": "Tenant B", "status": "active"},
                    {"id": tenant_suspended, "name": "Tenant Suspended", "status": "suspended"},
                ],
            )
            connection.execute(
                text("INSERT INTO tenant_memberships (id, tenant_id, user_id, role) VALUES (:id, :tenant_id, :user_id, 'analyst')"),
                [
                    {"id": uuid4(), "tenant_id": tenant_a, "user_id": user_a},
                    {"id": uuid4(), "tenant_id": tenant_b, "user_id": user_b},
                    {"id": uuid4(), "tenant_id": tenant_suspended, "user_id": user_suspended},
                ],
            )
            connection.execute(
                text("INSERT INTO audit_events (id, tenant_id, action, resource_type) VALUES (:id, :tenant_id, 'case.read', 'case')"),
                [{"id": uuid4(), "tenant_id": tenant_a}, {"id": uuid4(), "tenant_id": tenant_b}],
            )

        with Session(runtime_engine) as session:
            with authorized_tenant_transaction(session, tenant_a, user_a) as (scoped, role):
                assert role == "analyst"
                assert scoped.execute(text("SELECT name FROM tenants")).scalars().all() == ["Tenant A"]
                assert scoped.execute(text("SELECT user_id FROM tenant_memberships")).scalars().all() == [user_a]
                assert scoped.execute(text("SELECT tenant_id FROM audit_events")).scalars().all() == [tenant_a]

                # RLS rejects a cross-tenant insert even when the runtime role has INSERT permission.
                with pytest.raises(DBAPIError):
                    with scoped.begin_nested():
                        scoped.execute(
                            text("INSERT INTO audit_events (id, tenant_id, action, resource_type) VALUES (:id, :tenant_id, 'case.read', 'case')"),
                            {"id": uuid4(), "tenant_id": tenant_b},
                        )

                # Membership changes are reserved for a separate, privileged provisioning path.
                with pytest.raises(DBAPIError):
                    with scoped.begin_nested():
                        scoped.execute(
                            text("INSERT INTO tenant_memberships (id, tenant_id, user_id, role) VALUES (:id, :tenant_id, :user_id, 'analyst')"),
                            {"id": uuid4(), "tenant_id": tenant_a, "user_id": uuid4()},
                        )

                # Runtime role cannot rewrite existing audit evidence.
                with pytest.raises(DBAPIError):
                    with scoped.begin_nested():
                        scoped.execute(
                            text("UPDATE audit_events SET action = 'tampered' WHERE tenant_id = :tenant_id"),
                            {"tenant_id": tenant_a},
                        )

            # An authenticated user without membership cannot enter another tenant's scope.
            with pytest.raises(PermissionError, match="not a member"):
                with authorized_tenant_transaction(session, tenant_a, user_b):
                    pytest.fail("non-member must not enter tenant context")

            # Even a member cannot enter a suspended tenant's scope.
            with pytest.raises(PermissionError, match="Tenant is not active"):
                with authorized_tenant_transaction(session, tenant_suspended, user_suspended):
                    pytest.fail("suspended tenant must not grant access")

            # Transaction-local tenant context must be gone after commit or rollback.
            assert session.execute(text("SELECT count(*) FROM tenants")).scalar_one() == 0
            assert session.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 0
            session.rollback()
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()
