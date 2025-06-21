import pytest
import requests
from automation_assistant.main import login_and_fetch_session, fetch_workflows

class DummyResponse:
    def __init__(self, data=None, status_code=200):
        self._data = data or []
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError(f"Status code: {self.status_code}")

    def json(self):
        return {'data': self._data}

class DummySession:
    def __init__(self, login_ok=True, workflows=None):
        self.login_ok = login_ok
        self._workflows = workflows or []

    def post(self, url, data=None, headers=None):
        return DummyResponse(status_code=200 if self.login_ok else 401)

    def get(self, url):
        return DummyResponse(data=self._workflows, status_code=200)

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("N8N_API_URL", "http://fake:5678")
    monkeypatch.setenv("N8N_USER_EMAIL", "u@e.com")
    monkeypatch.setenv("N8N_USER_PASSWORD", "pass")

def test_login_and_fetch_workflows(monkeypatch):
    dummy = DummySession(login_ok=True, workflows=[{"id": 1, "name": "TestWF"}])
    monkeypatch.setattr(requests, "Session", lambda: dummy)

    sess = login_and_fetch_session("http://fake:5678", "u@e.com", "pass")
    assert sess is dummy

    result = fetch_workflows(sess, "http://fake:5678")
    assert result == [{"id": 1, "name": "TestWF"}]

def test_login_failure(monkeypatch):
    dummy = DummySession(login_ok=False)
    monkeypatch.setattr(requests, "Session", lambda: dummy)
    with pytest.raises(requests.HTTPError):
        login_and_fetch_session("http://fake:5678", "u@e.com", "wrong")

def test_fetch_failure(monkeypatch):
    class BadSession(DummySession):
        def get(self, url):
            raise requests.HTTPError("fetch error")
    bad = BadSession()
    monkeypatch.setattr(requests, "Session", lambda: bad)
    sess = login_and_fetch_session("http://fake:5678", "u@e.com", "pass")
    with pytest.raises(requests.HTTPError):
        fetch_workflows(sess, "http://fake:5678")
