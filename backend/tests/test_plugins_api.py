"""Tests for plugins API."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
import json
import subprocess

import app.main
import app.config


@pytest.fixture
def client_with_repo():
    """Create test client with temporary repository."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test-repo"

    repo_path.mkdir()
    (repo_path / "plugins").mkdir()
    (repo_path / "ratings").mkdir()

    marketplace = {
        "name": "test-marketplace",
        "display_name": "Test",
        "description": "Test",
        "owner": {"name": "Test", "email": "test@test.com"},
        "created_at": "2026-04-14",
        "plugins_count": 0
    }
    with open(repo_path / "marketplace.json", "w") as f:
        json.dump(marketplace, f)

    # Create a test plugin
    plugin_dir = repo_path / "plugins" / "test-plugin" / ".claude-plugin"
    plugin_dir.mkdir(parents=True)
    plugin_json = {
        "name": "test-plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "author": {"name": "Test Author", "email": "author@test.com"}
    }
    with open(plugin_dir / "plugin.json", "w") as f:
        json.dump(plugin_json, f)

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_path, check=True,
                   capture_output=True)

    # Override settings
    app.config.settings.plugins_repo_path = repo_path

    client = TestClient(app.main.app)
    yield client

    shutil.rmtree(temp_dir)


class TestPluginsAPI:
    """Tests for plugins endpoints."""

    def test_list_plugins(self, client_with_repo):
        """Test listing plugins."""
        response = client_with_repo.get("/api/plugins/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test-plugin"

    def test_get_plugin(self, client_with_repo):
        """Test getting a specific plugin."""
        response = client_with_repo.get("/api/plugins/test-plugin")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-plugin"
        assert data["description"] == "A test plugin"

    def test_get_plugin_not_found(self, client_with_repo):
        """Test getting non-existent plugin."""
        response = client_with_repo.get("/api/plugins/nonexistent")
        assert response.status_code == 404

    def test_sync_status(self, client_with_repo):
        """Test sync status endpoint."""
        response = client_with_repo.get("/api/sync/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_plugins" in data

    def test_health(self, client_with_repo):
        """Test health check."""
        response = client_with_repo.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
