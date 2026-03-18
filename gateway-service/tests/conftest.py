"""
Shared pytest fixtures for gateway-service tests.
All Supabase and external service calls are mocked so tests run without credentials.
"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure the gateway-service root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True, scope="session")
def mock_supabase_env():
    """Inject dummy environment variables before any module is imported."""
    with patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://mock.supabase.co",
            "SUPABASE_KEY": "mock_key_for_tests",
            "PROCESSING_SERVICE_URL": "http://localhost:8001",
        },
    ):
        yield


@pytest.fixture(scope="session")
def mock_supabase_client():
    """Return a MagicMock replacing the supabase client used in config.py."""
    with patch("config.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client
