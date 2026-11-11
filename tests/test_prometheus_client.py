from types import SimpleNamespace

import pytest
import requests

from app.prometheus.api_client import PrometheusAPI, PrometheusError


def test_http_error_does_not_include_response_body() -> None:
    response = SimpleNamespace(status_code=502, text="internal marker=do-not-leak")

    with pytest.raises(PrometheusError) as error:
        PrometheusAPI("http://prometheus.internal")._handle_response(response)

    assert str(error.value) == "Prometheus HTTP 502"
    assert "do-not-leak" not in str(error.value)


def test_request_error_does_not_include_url_or_original_message(monkeypatch) -> None:
    def fail_request(*args, **kwargs):
        raise requests.RequestException("internal marker=do-not-leak")

    monkeypatch.setattr("app.prometheus.api_client.requests.get", fail_request)

    with pytest.raises(PrometheusError) as error:
        PrometheusAPI("http://prometheus.internal").query("up")

    assert str(error.value) == "Prometheus request failed"
    assert "prometheus.internal" not in str(error.value)
    assert "do-not-leak" not in str(error.value)
