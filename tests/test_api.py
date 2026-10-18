from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_health_returns_overall_status():
    r = client.get("/health")
    assert r.status_code == 200
    assert "overall_status" in r.json()
    assert "timestamp" in r.json()


def test_metrics_returns_metrics_list():
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "metrics" in data
    assert isinstance(data["metrics"], list)


def test_cors_allows_configured_origin():
    r = client.get("/health", headers={"Origin": "https://euchelu.github.io"})
    assert r.headers["access-control-allow-origin"] == "https://euchelu.github.io"


def test_cors_rejects_unknown_origin():
    # Un origen fuera de ALLOWED_ORIGINS no debe recibir la cabecera CORS.
    r = client.get("/health", headers={"Origin": "https://sitio-no-autorizado.com"})
    assert "access-control-allow-origin" not in r.headers
