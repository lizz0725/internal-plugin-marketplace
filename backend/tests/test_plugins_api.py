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
    (repo_path / "pending" / "submissions").mkdir(parents=True)
    (repo_path / "ratings").mkdir()
    (repo_path / "reviews").mkdir()
    (repo_path / "stats").mkdir()

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

    def test_list_plugins_empty(self, client_with_repo):
        """Test listing empty plugins."""
        response = client_with_repo.get("/api/plugins/")
        assert response.status_code == 200
        assert response.json() == []

    def test_submit_plugin(self, client_with_repo):
        """Test submitting a plugin."""
        payload = {
            "plugin": {
                "name": "test-plugin",
                "description": "Test Description",
                "version": "1.0.0",
                "author": {"name": "Test Author", "email": "author@test.com"},
                "keywords": ["test"]
            },
            "submitter": {
                "name": "Submitter",
                "email": "submitter@test.com",
                "submitted_at": "2026-04-14T10:00:00Z",
                "message": "Test submission"
            }
        }

        response = client_with_repo.post("/api/plugins/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "submission_id" in data
        assert data["status"] == "pending"

    def test_get_plugin_not_found(self, client_with_repo):
        """Test getting non-existent plugin."""
        response = client_with_repo.get("/api/plugins/nonexistent")
        assert response.status_code == 404

    def test_submit_duplicate_plugin(self, client_with_repo):
        """Test submitting duplicate plugin fails."""
        payload = {
            "plugin": {
                "name": "duplicate-plugin",
                "description": "Test Description",
                "version": "1.0.0",
                "author": {"name": "Test Author", "email": "author@test.com"}
            },
            "submitter": {
                "name": "Submitter",
                "email": "submitter@test.com",
                "submitted_at": "2026-04-14T10:00:00Z"
            }
        }

        # First submission should succeed
        response1 = client_with_repo.post("/api/plugins/submit", json=payload)
        assert response1.status_code == 200

        # Second submission should fail
        response2 = client_with_repo.post("/api/plugins/submit", json=payload)
        assert response2.status_code == 400