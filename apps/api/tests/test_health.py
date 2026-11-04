from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from omni_api import main

client = TestClient(main.app)


def test_health_reports_liveness() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "omni-engine-api",
        "version": "0.2.0",
    }


def test_readiness_reports_database_available(monkeypatch) -> None:
    monkeypatch.setattr(main, "check_database", lambda: True)
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_readiness_fails_closed_when_database_is_unavailable(monkeypatch) -> None:
    def unavailable() -> bool:
        raise OperationalError("SELECT 1", {}, RuntimeError("database offline"))

    monkeypatch.setattr(main, "check_database", unavailable)
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable"}
