from fastapi.testclient import TestClient

from app.api import main


def test_health_does_not_expose_prometheus_endpoint() -> None:
    response = TestClient(main.app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_trained": main.detector.is_trained,
    }
    assert "prometheus_url" not in response.json()


def test_detect_hides_internal_runtime_errors(monkeypatch) -> None:
    class FailingDetector:
        is_trained = True

        def detect_current(self):
            raise RuntimeError("internal prometheus token")

    monkeypatch.setattr(main, "detector", FailingDetector())

    response = TestClient(main.app).get("/detect")

    assert response.status_code == 500
    assert response.json()["detail"] == "Anomaly detection failed."
    assert "internal prometheus token" not in response.text
