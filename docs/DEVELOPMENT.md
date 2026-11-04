# Development Setup

## Prerequisites
- Git
- Docker Desktop with Docker Compose
- Python 3.12+ for local API tests
- Node.js 22+ and npm for local web development

## Local environment
1. From the repository root, copy `.env.example` to `.env`.
2. Set two different strong local-only passwords: `POSTGRES_PASSWORD` for the database administrator and `OMNI_APP_DB_PASSWORD` for the restricted API role.
3. Start services with `docker compose up --build -d`.
4. The PostgreSQL initialization script creates `omni_app` with `NOBYPASSRLS`; the API receives only this role's connection string.
5. Apply the schema migration from the repository root. In PowerShell:

```powershell
$env:OMNI_MIGRATION_DATABASE_URL = "postgresql+psycopg://omni_admin:$env:POSTGRES_PASSWORD@db:5432/omni_engine"
docker compose exec -e OMNI_MIGRATION_DATABASE_URL=$env:OMNI_MIGRATION_DATABASE_URL api alembic upgrade head
Remove-Item Env:OMNI_MIGRATION_DATABASE_URL
```

The migration credential is supplied only to the one-off Alembic process. It is not part of the running API service environment. If `POSTGRES_USER` or `POSTGRES_DB` differs from the defaults, adjust the migration URL accordingly.

6. Open the web app at http://localhost:3000, API liveness at http://localhost:8000/api/v1/health, and database readiness at http://localhost:8000/api/v1/ready.

The database schema is not created automatically when the API starts. Run Alembic migrations explicitly with the privileged migration credential.

## API tests
From the repository root:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
ruff check apps/api
```

## Web application
From `apps/web`:

```powershell
npm install
npm run lint
npm run build
npm run dev
```

The first npm install generates a lockfile. Commit that lockfile before enabling reproducible web CI.

## Safety
Do not use real consumer reports or unmasked PII in this foundation build. Authentication, tenant membership enforcement at the API boundary, encryption, malware scanning, protected document storage, retention controls, and PostgreSQL cross-tenant integration tests are prerequisites for production data.
