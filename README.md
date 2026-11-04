# OMNI-ENGINE

**Enterprise Credit Intelligence & Financial Optimization Platform**

OMNI-ENGINE is an independent platform for evidence-based credit intelligence, regulatory research, dispute workflow support, financial education, and scenario analysis.

## Engineering principles

- Evidence before conclusions: material findings must retain source and evidence provenance.
- Legal authority classification: statutes, regulations, court decisions, agency guidance, enforcement materials, and industry standards are distinct source classes.
- Version-aware research: retain publication dates, effective dates, retrieval timestamps, and content hashes.
- Human approval: external submissions and consequential actions require explicit human review.
- Privacy by design: minimize sensitive data, isolate tenants, encrypt secrets and personal data, and audit access.
- Explainability: recommendations must identify assumptions, limitations, and supporting sources.

## Architecture

- `apps/web`: Next.js App Router and TypeScript interface.
- `apps/api`: FastAPI service and domain modules.
- `packages/contracts`: shared API contracts and schemas (planned).
- `infra`: Docker Compose and deployment assets.
- `docs`: architecture, security, governance, and decision records.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local setup and test commands. Copy `.env.example` to `.env` and replace development-only values before running services.

## Current scope

This repository establishes the platform foundation. It does not yet provide production credit scoring, bureau connectivity, legal advice, or automated dispute submission. Credit-score projections must be labeled estimates and must not imply guaranteed outcomes.

## Independence

OMNI-ENGINE is a standalone product. It has no CDOS dependency, integration, shared runtime, or inherited code requirement.
