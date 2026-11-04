"""PostgreSQL integration tests; skipped unless CI supplies isolated test URLs."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

ADMIN_URL = os.getenv("OMNI_TEST_ADMIN_DATABASE_URL")
RUNTIME_URL = os.getenv("OMNI_TEST_RUNTIME_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not ADMIN_URL or not RUNTIME_URL,
    reason="PostgreSQL RLS integration URLs are not configured",
)


def test_runtime_role_is_tenant_isolated_and_audit_is_append_only() -> None:
    admin_engine = create_engine(ADMIN_URL, future=True)
    runtime_engine = create_engine(RUNTIME_URL, future=True)
    tenant_a, tenant_b = uuid4(), uuid4()
    user_a, user_b = uuid4(), uuid4()

    try:
        with admin_engine.begin() as connection:
            connection.execute(
                text("INSERT INTO tenants (id, name, status) VALUES (:id, :name, 'active')"),
                [{"id": tenant_a, "name": "Tenant A"}, {"id": tenant_b, "name": "Tenant B"}],
            )
            connection.execute(
                text("INSERT INTO tenant_memberships (id, tenant_id, user_id, role) VALUES (:id, :tenant_id, :user_id, 'analyst')"),
                [
                    {"id": uuid4(), "tenant_id": tenant_a, "user_id": user_a},
                    {"id": uuid4(), "tenant_id": tenant_b, "user_id": user_b},
                ],
            )
            connection.execute(
                text("INSERT INTO audit_events (id, tenant_id, action, resource_type) VALUES (:id, :tenant_id, 'case.read', 'case')"),
                [{"id": uuid4(), "tenant_id": tenant_a}, {"id": uuid4(), "tenant_id": tenant_b}],
            )

        with runtime_engine.connect() as connection:
            with connection.begin():
                assert connection.execute(text("SELECT count(*) FROM tenants")).scalar_one() == 0
                assert connection.execute(text("SELECT count(*) FROM tenant_memberships")).scalar_one() == 0
                assert connection.execute(text("SELECT count(*) FROM audit_events")).scalar_one() == 0

                connection.execute(
                    text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                    {"tenant_id": str(tenant_a)},
                )
                assert connection.execute(text("SELECT name FROM tenants")).scalars().all() == ["Tenant A"]
                assert connection.execute(text("SELECT user_id FROM tenant_memberships")).scalars().all() == [user_a]
                assert connection.execute(text("SELECT tenant_id FROM audit_events")).scalars().all() == [tenant_a]

                with pytest.raises(DBAPIError):
                    with connection.begin_nested():
                        connection.execute(
                            text("INSERT INTO tenant_memberships (id, tenant_id, user_id, role) VALUES (:id, :tenant_id, :user_id, 'analyst')"),
                            {"id": uuid4(), "tenant_id": tenant_b, "user_id": uuid4()},
                        )

                with pytest.raises(DBAPIError):
                    with connection.begin_nested():
                        connection.execute(
                            text("UPDATE audit_events SET action = 'tampered' WHERE tenant_id = :tenant_id"),
                            {"tenant_id": tenant_a},
                        )
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()
