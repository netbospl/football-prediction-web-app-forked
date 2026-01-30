"""Pytest configuration and shared fixtures."""

import os
import sys
import pytest
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def temp_data_dir():
    """Create a temporary data directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config(temp_data_dir, monkeypatch):
    """Mock config to use temporary directories."""
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("DATA_DIR", temp_data_dir)
    monkeypatch.setenv("DB_PATH", os.path.join(temp_data_dir, "test.db"))

    # Reload config module to pick up new values
    from src.utils import config
    import importlib
    importlib.reload(config)

    yield config.Config

    # Cleanup
    importlib.reload(config)
