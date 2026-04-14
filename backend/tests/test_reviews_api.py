"""Tests for reviews API."""
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
def client_with_submission():
    """Create test client with a pending submission."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test-repo"

    repo_path.mkdir()
    (repo_path / "plugins").mkdir()
    (repo_path / "pending" / "submissions").mkdir(parents=True)
    (repo_path / "ratings").mkdir()
    (repo_path / "reviews").mkdir()
    (repo_path / "stats").mkdir()

    marketplace = {
        "name": "test",
        "display_name": "Test",
        "description": "Test",
        "owner": {"name": "Test", "email": "test@test.com"},
        "created_at": "2026-04-14",
        "plugins_count": 0
    }
    with open(repo_path / "marketplace.json", "w") as f:
        json.dump(marketplace, f)

    # Create a submission
    submission_dir = repo_path / "pending" / "submissions" / "test-001"
    submission_dir.mkdir()

    plugin_data = {
        "name": "pending-plugin",
        "description": "Pending Plugin",
        "version": "1.0.0",
        "author": {"name": "Author", "email": "author@test.com"}
    }
    submitter_data = {
        "name": "Submitter",
        "email": "submitter@test.com",
        "submitted_at": "2026-04-14T10:00:00Z"
    }
    review_data = {
        "submission_id": "test-001",
        "status": "pending"
    }

    with open(submission_dir / "plugin.json", "w") as f:
        json.dump(plugin_data, f)
    with open(submission_dir / "submitter.json", "w") as f:
        json.dump(submitter_data, f)
    with open(submission_dir / "review_status.json", "w") as f:
        json.dump(review_data, f)

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_path, check=True,
                   capture_output=True)

    app.config.settings.plugins_repo_path = repo_path

    client = TestClient(app.main.app)
    yield client

    shutil.rmtree(temp_dir)


class TestReviewsAPI:
    """Tests for reviews endpoints."""

    def test_get_pending_reviews(self, client_with_submission):
        """Test getting pending reviews."""
        response = client_with_submission.get("/api/reviews/pending")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["submission_id"] == "test-001"

    def test_approve_submission(self, client_with_submission):
        """Test approving a submission."""
        response = client_with_submission.post(
            "/api/reviews/test-001/approve",
            json={"reviewer_email": "admin@test.com", "notes": "Good"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["plugin_name"] == "pending-plugin"

    def test_reject_submission(self, client_with_submission):
        """Test rejecting a submission."""
        response = client_with_submission.post(
            "/api/reviews/test-001/reject",
            json={"reviewer_email": "admin@test.com", "reason": "Not good"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    def test_approve_nonexistent_submission(self, client_with_submission):
        """Test approving a nonexistent submission."""
        response = client_with_submission.post(
            "/api/reviews/nonexistent/approve",
            json={"reviewer_email": "admin@test.com", "notes": "Good"}
        )
        assert response.status_code == 404

    def test_approve_already_processed(self, client_with_submission):
        """Test approving an already processed submission."""
        # First approve
        client_with_submission.post(
            "/api/reviews/test-001/approve",
            json={"reviewer_email": "admin@test.com", "notes": "Good"}
        )
        # Try to approve again
        response = client_with_submission.post(
            "/api/reviews/test-001/approve",
            json={"reviewer_email": "admin@test.com", "notes": "Good"}
        )
        assert response.status_code == 400