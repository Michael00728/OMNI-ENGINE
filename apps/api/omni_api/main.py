"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from omni_api.config import get_settings

settings = get_settings()

app = FastAPI(
    title="OMNI-ENGINE API",
    description=(
        "Foundation API for evidence-based credit intelligence. "
        "Automated findings are informational and require appropriate human review."
    ),
    version="0.1.0",
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
    return {"status": "ok", "service": "omni-engine-api", "version": "0.1.0"}
