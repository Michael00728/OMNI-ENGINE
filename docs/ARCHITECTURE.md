# OMNI-ENGINE Architecture Baseline

## System boundaries
OMNI-ENGINE is a standalone application. Its source tree, dependency graph, deployment configuration, data stores, CI workflows, and runtime are owned by this repository. No external project is an architectural prerequisite.

## Initial topology
- Web: Next.js App Router and TypeScript in `apps/web`.
- API: FastAPI in `apps/api`; domain logic belongs in explicit modules rather than route handlers.
- Persistence: PostgreSQL is provisioned by Compose. Database access, migrations, and tenant enforcement are deferred until their security model is implemented and tested.
- Knowledge: source metadata and authority taxonomy are established in `omni_api.knowledge`; acquisition, parsing, indexing, and retrieval are subsequent increments.
- Operations: Docker Compose for local services; GitHub Actions for API quality checks.

## Planned domain modules
1. Regulatory source registry and version history.
2. Document ingestion, malware scanning, extraction, and evidence vault.
3. Credit report normalization and bureau reconciliation.
4. Findings, dispute case workflow, and deadline management.
5. Financial education and scenario forecasting.
6. Tenant administration, authorization, audit, and reporting.

## Evidence provenance contract
Every ingested source version should preserve a stable source identifier, canonical URL, publisher, authority class, legal-force classification, jurisdiction, publication/effective dates where available, retrieval timestamp, cryptographic content hash, and precise citation locator. A content hash establishes byte-level identity, not legal authenticity or correctness.

## Authority distinctions
Statutes, regulations, court decisions, agency guidance, enforcement actions, educational materials, and industry standards are separate categories. Industry formats or workflows must not be described as statutes or regulations. Applicability requires jurisdiction, facts, dates, and qualified review.

## High-impact action boundary
The platform may organize evidence and draft recommendations. External submissions, legal assertions, account actions, and other consequential operations require explicit user authorization and human review. No autonomous external submission is part of this foundation.

## Forecasting boundary
Credit-score and lending outcomes are uncertain. Forecasts must disclose assumptions, model limitations, data gaps, and the fact that bureau files, proprietary scoring models, lender criteria, and timing can change outcomes.
