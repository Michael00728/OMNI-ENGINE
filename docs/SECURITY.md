# Security Baseline

## Implemented foundation controls
- Configuration is environment-driven; credentials are not committed.
- CORS uses explicit origins and rejects wildcard configuration.
- The API container runs as a non-root user.
- PostgreSQL is not published to the host by default.
- PostgreSQL has separate administrative and API runtime roles. The API receives only the runtime password.
- The API role is created with `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, and `NOBYPASSRLS`.
- Tenant tables use PostgreSQL row-level security (RLS), enabled and forced.
- RLS denies access when transaction-local `app.tenant_id` is absent.
- Tenant context is set with transaction-local `set_config`; it clears automatically at transaction end.
- Audit events are append-only for the runtime role: it receives SELECT and INSERT, not UPDATE or DELETE.
- Alembic requires a separately supplied privileged migration URL; the API process does not receive that credential.
- GitHub Actions uses read-only repository permissions for CI.

## Tenant context security contract

The `tenant_transaction` helper accepts a tenant UUID and applies it to the current PostgreSQL transaction. It is not an authentication mechanism. Production request handlers must obtain the tenant identifier from a verified authenticated principal and validate the user's active membership before entering the helper. Never trust an unverified tenant ID from a request header, URL parameter, or request body. No client-facing tenant data endpoints are enabled in this increment.

## Required before production or real consumer data
1. Implement authentication, authorization, tenant-scoped access checks, and tested role policies.
2. Add encryption at rest and in transit, managed key rotation, and secret-manager integration.
3. Add malware scanning and quarantine before document parsing; fail closed if scanning is unavailable.
4. Add PII minimization, field-level protection, retention schedules, deletion workflows, and audit access trails.
5. Add database backups, restore drills, and PostgreSQL integration tests proving cross-tenant isolation with the actual runtime role.
6. Add dependency, container, secret, and static-analysis scanning in CI.
7. Complete threat modeling, incident response, and privacy impact review.

Audit metadata must contain operational facts only; do not store SSNs, full account numbers, credentials, raw credit report text, or unnecessary personal data in audit JSON.

This foundation is not certified, production hardened, or approved for real consumer credit reports or unmasked identity data. Never commit credentials, SSNs, full account numbers, or consumer documents.
