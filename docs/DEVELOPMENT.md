# Development Setup

## Prerequisites
- Git
- Docker Desktop with Docker Compose
- Python 3.12+ for local API tests
- Node.js 22+ and npm for local web development

## Local environment
1. From the repository root, copy `.env.example` to `.env`.
2. Set three different local-only passwords: `POSTGRES_PASSWORD` for the database administrator, `OMNI_MIGRATOR_DB_PASSWORD` for the non-superuser migration role, and `OMNI_APP_DB_PASSWORD` for the restricted API runtime role. Keep the migration and runtime passwords URL-safe (letters, digits, `_`, and `-`) because they are embedded in database connection URLs.
3. Start services with `docker compose up --build -d`.
4. The PostgreSQL initialization script creates `omni_migrator` and `omni_app`. The API receives only the `omni_app` connection string.
5. Apply the schema migration from the repository root. In PowerShell, read the migration password from `.env` and pass it only to the one-off Alembic process:

```powershell
$migratorPassword = ((Get-Content .env | Where-Object { $_ -match '^OMNI_MIGRATOR_DB_PASSWORD=' } | Select-Object -First 1) -replace '^OMNI_MIGRATOR_DB_PASSWORD=', '').Trim('"')
if (-not $migratorPassword) { throw 'OMNI_MIGRATOR_DB_PASSWORD was not found in .env' }
$env:OMNI_MIGRATION_DATABASE_URL = "postgresql+psycopg://omni_migrator:${migratorPassword}@db:5432/omni_engine"
docker compose exec -e OMNI_MIGRATION_DATABASE_URL=$env:OMNI_MIGRATION_DATABASE_URL api alembic upgrade head
Remove-Item Env:OMNI_MIGRATION_DATABASE_URL
Remove-Variable migratorPassword
```

The migration credential is supplied only to the one-off Alembic process. It is not part of the running API service environment. If `POSTGRES_DB` differs from `omni_engine`, adjust the migration URL accordingly.

6. Open the web app at http://localhost:3000, API liveness at http://localhost:8000/api/v1/health, and database readiness at http://localhost:8000/api/v1/ready.

The database schema is not created automatically when the API starts. Run Alembic migrations explicitly with the dedicated migration-role credential.

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
Do not use real consumer reports or unmasked PII in this foundation build. Authentication, authorization, encryption, malware scanning, protected document storage, retention controls, and operational restore procedures are prerequisites for production data.
