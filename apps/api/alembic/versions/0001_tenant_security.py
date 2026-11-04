"""Create tenant tables, PostgreSQL row-level security, and append-only audit log.

Revision ID: 0001_tenant_security
Revises:
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_tenant_security"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('active', 'suspended', 'closed')", name="ck_tenants_status_valid"),
        sa.PrimaryKeyConstraint("id", name="pk_tenants"),
    )
    op.create_table(
        "tenant_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('owner', 'admin', 'analyst', 'read_only')", name="ck_tenant_memberships_role_valid"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE", name="fk_tenant_memberships_tenant_id_tenants"),
        sa.PrimaryKeyConstraint("id", name="pk_tenant_memberships"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),
    )
    op.create_index("ix_memberships_user_id", "tenant_memberships", ["user_id"], unique=False)
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=200), nullable=True),
        sa.Column("event_metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(action) BETWEEN 1 AND 120", name="ck_audit_events_action_length_valid"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT", name="fk_audit_events_tenant_id_tenants"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index("ix_audit_events_tenant_created", "audit_events", ["tenant_id", "created_at"], unique=False)
    op.create_index("ix_audit_events_tenant_resource", "audit_events", ["tenant_id", "resource_type", "resource_id"], unique=False)

    # RLS is forced even for table owners. The API runtime must use a separate NOBYPASSRLS role.
    for table in ("tenants", "tenant_memberships", "audit_events"):
        op.execute(sa.text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY'))
        op.execute(sa.text(
            f'''CREATE POLICY tenant_isolation ON "{table}"
            USING (
                {"id" if table == "tenants" else "tenant_id"} =
                NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
            WITH CHECK (
                {"id" if table == "tenants" else "tenant_id"} =
                NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )'''
        ))

    # The runtime role has read/write access to tenant data, but audit records are insert/read only.
    op.execute("GRANT SELECT ON tenants TO omni_app")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_memberships TO omni_app")
    op.execute("GRANT SELECT, INSERT ON audit_events TO omni_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON audit_events")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON tenant_memberships")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON tenants")
    op.drop_index("ix_audit_events_tenant_resource", table_name="audit_events")
    op.drop_index("ix_audit_events_tenant_created", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_memberships_user_id", table_name="tenant_memberships")
    op.drop_table("tenant_memberships")
    op.drop_table("tenants")
