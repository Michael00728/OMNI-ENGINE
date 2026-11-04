# Development Setup

## Prerequisites
- Git
- Docker Desktop with Docker Compose
- Python 3.12+ for local API tests
- Node.js 22+ and npm for local web development

## Local environment
1. From the repository root, copy `.env.example` to `.env`.
2. Replace the local PostgreSQL password in `.env`; do not reuse production credentials.
3. Start services with `docker compose up --build`.
4. Open the web app at http://localhost:3000 and API health at http://localhost:8000/api/v1/health.

The database container is provisioned, but application persistence and migrations are not implemented in this foundation increment.

## API tests
From the repository root:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
ruff check apps/api
```

## Web application
From `apps/web`:

```bash
npm install
npm run lint
npm run build
npm run dev
```

The first npm install generates a lockfile. Commit that lockfile before enabling reproducible web CI.

## Safety
Do not use real consumer reports or unmasked PII in this foundation build. Authentication, tenant isolation, document malware scanning, protected storage, and retention controls are prerequisites for production data.
