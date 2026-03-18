"""
Unit tests for the InfraSight Gateway Service.
Supabase and the processing service are mocked.
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_client():
    with patch.dict(
        os.environ,
        {"SUPABASE_URL": "https://mock.supabase.co", "SUPABASE_KEY": "mock_key"},
    ):
        with patch("supabase.create_client", return_value=MagicMock()):
            from fastapi.testclient import TestClient
            import importlib
            import config as cfg

            cfg.supabase = MagicMock()
            import main
            importlib.reload(main)
            return TestClient(main.app)


@pytest.fixture(scope="module")
def client():
    return _make_client()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_docs_accessible(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/health" in schema["paths"]
    assert "/auth/login" in schema["paths"]
    assert "/images/upload" in schema["paths"]


def test_login_invalid_credentials(client):
    """Login with bad credentials should return 401."""
    import config as cfg

    cfg.supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
    response = client.post(
        "/auth/login", json={"email": "bad@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_signup_bad_email(client):
    """Signup with a malformed email should return 422 (validation error)."""
    response = client.post(
        "/auth/signup", json={"email": "not-an-email", "password": "password123"}
    )
    assert response.status_code == 422
