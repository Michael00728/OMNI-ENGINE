from fastapi.testclient import TestClient

from omni_api.main import app

client = TestClient(app)


def test_health_reports_liveness() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "omni-engine-api",
        "version": "0.1.0",
    }
