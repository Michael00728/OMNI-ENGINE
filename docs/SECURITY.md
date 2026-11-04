# Security Baseline

## Current controls
- Configuration is environment-driven; real credentials are excluded from version control.
- CORS uses explicit origins and rejects wildcard configuration.
- The API container runs as a non-root user.
- The database is not published to the host by default.
- GitHub Actions uses read-only repository permissions for API CI.
- Source metadata rejects non-HTTPS canonical URLs and malformed SHA-256 digests.

## Required before production or real consumer data
1. Implement authentication, authorization, tenant-scoped access checks, and tested role policies.
2. Add encryption at rest and in transit, managed key rotation, and secret-manager integration.
3. Add malware scanning and quarantine before document parsing; fail closed if scanning is unavailable.
4. Add PII minimization, field-level protection, retention schedules, deletion workflows, and access audit trails.
5. Add database migrations, backups, restore drills, and tenant isolation tests.
6. Add dependency, container, secret, and static-analysis scanning in CI.
7. Complete threat modeling, incident response, and privacy impact review.

This foundation is not certified, production hardened, or approved for real consumer credit reports or unmasked identity data. Never commit credentials, SSNs, full account numbers, or consumer documents.
