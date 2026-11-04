# Security Baseline

## Implemented foundation controls
- Configuration is environment-driven; credentials are not committed.
- CORS uses explicit origins and rejects wildcard configuration.
- The API container runs as a non-root user.
- PostgreSQL is not published to the host by default.
- PostgreSQL separates the database administrator, Alembic migration role, and API runtime role.
- The API receives only the `omni_app` connection string; it never receives administrator or migration credentials.
- The migration role is a non-superuser with schema creation rights for controlled migrations, not a superuser.
- The API role is created with `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, and `NOBYPASSRLS`.
- Tenant tables use PostgreSQL row-level security (RLS), enabled and forced.
- RLS denies access when transaction-local `app.tenant_id` is absent.
- Tenant context is set with transaction-local `set_config`; it clears automatically at transaction end.
- `authorized_tenant_transaction` verifies that the tenant is active and the authenticated user has a membership under the selected tenant RLS context before yielding access.
- Tenant and membership records are read-only to the API runtime; tenant provisioning is a separate privileged operation.
- Audit events are append-only for the runtime role: it receives SELECT and INSERT, not UPDATE or DELETE.
- Alembic requires a separately supplied migration-role URL; the API process does not receive that credential.
- GitHub Actions runs migrations with the migration role and PostgreSQL integration tests with the restricted runtime role.

## Tenant context security contract

Authentication is not implemented in this foundation. Future request handlers must derive `authenticated_user_id` from a verified identity token or session, never from a caller-controlled field. The selected tenant ID is not trusted by itself. Use `authorized_tenant_transaction(session, tenant_id, authenticated_user_id)`: it sets transaction-local RLS context, verifies that the tenant is active, checks the user's membership inside that tenant scope, and refuses to yield if either condition fails. Do not use the lower-level `tenant_transaction` helper directly in client-facing handlers. Never trust an unverified tenant ID from a request header, URL parameter, or request body. No client-facing tenant data endpoints are enabled in this increment.

## Required before production or real consumer data
1. Implement authentication, authorization, role-based permission checks, and API request protections around the authorized tenant transaction helper.
2. Add encryption at rest and in transit, managed key rotation, and secret-manager integration.
3. Add malware scanning and quarantine before document parsing; fail closed if scanning is unavailable.
4. Add PII minimization, field-level protection, retention schedules, deletion workflows, and audit access trails.
5. Add database backups, restore drills, and operational monitoring; keep PostgreSQL cross-tenant integration tests passing in CI.
6. Add dependency, container, secret, and static-analysis scanning in CI.
7. Complete threat modeling, incident response, and privacy impact review.

Audit metadata must contain operational facts only; do not store SSNs, full account numbers, credentials, raw credit report text, or unnecessary personal data in audit JSON.

This foundation is not certified, production hardened, or approved for real consumer credit reports or unmasked identity data. Never commit credentials, SSNs, full account numbers, or consumer documents.
