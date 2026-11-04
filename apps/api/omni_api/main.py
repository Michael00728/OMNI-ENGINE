"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from omni_api.config import get_settings
from omni_api.db.session import check_database

settings = get_settings()

app = FastAPI(
    title="OMNI-ENGINE API",
    description=(
        "Foundation API for evidence-based credit intelligence. "
        "Automated findings are informational and require appropriate human review."
    ),
    version="0.2.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.get("/api/v1/health", tags=["operations"])
def health() -> dict[str, str]:
    """Return process liveness; this endpoint does not assert database readiness."""
    return {"status": "ok", "service": "omni-engine-api", "version": "0.2.0"}


@app.get("/api/v1/ready", tags=["operations"])
def readiness() -> dict[str, str]:
    """Return ready only when the database is reachable and schema is current."""
    try:
        if not check_database():
            raise SQLAlchemyError("Database schema is not at the expected migration revision")
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database or schema is not ready",
        ) from exc
    return {"status": "ready", "database": "ok", "schema": "current"}
