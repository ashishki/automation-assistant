import pytest
from automation_assistant.main import fetch_workflows

class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"Status code: {self.status_code}")

def test_fetch_workflows_success(monkeypatch):
    # arrange
    dummy_data = [{"id": 1, "name": "Test"}]
    def fake_get(url, headers):
        assert "workflows" in url
        assert "Authorization" in headers
        return DummyResponse(dummy_data)

    monkeypatch.setattr("requests.get", fake_get)

    # act
    result = fetch_workflows("http://example:5678/rest", "fake-key")

    # assert
    assert result == dummy_data

def test_fetch_workflows_failure(monkeypatch):
    # simulate non-200 status
    def fake_get(url, headers):
        return DummyResponse(None, status_code=500)

    monkeypatch.setattr("requests.get", fake_get)

    with pytest.raises(Exception):
        fetch_workflows("http://example:5678/rest", "fake-key")
