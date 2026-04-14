"""Tests for git_ops module."""
import pytest
from pathlib import Path
import tempfile
import shutil
import json

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import PluginMetadata, Author, SubmitterInfo, ReviewStatus, Submission, Rating


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test-repo"

    # Create structure
    repo_path.mkdir()
    (repo_path / "plugins").mkdir()
    (repo_path / "pending" / "submissions").mkdir(parents=True)
    (repo_path / "ratings").mkdir()
    (repo_path / "reviews").mkdir()
    (repo_path / "stats").mkdir()

    # Create marketplace.json
    marketplace = {
        "name": "test-marketplace",
        "display_name": "Test Marketplace",
        "description": "Test",
        "owner": {"name": "Test", "email": "test@test.com"},
        "created_at": "2026-04-14",
        "plugins_count": 0
    }
    with open(repo_path / "marketplace.json", "w") as f:
        json.dump(marketplace, f)

    # Init git
    import subprocess
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_path, check=True,
                   capture_output=True)

    yield repo_path

    shutil.rmtree(temp_dir)


class TestGitRepoReader:
    """Tests for GitRepoReader."""

    def test_get_marketplace_meta(self, temp_repo):
        """Test reading marketplace metadata."""
        reader = GitRepoReader(temp_repo)
        meta = reader.get_marketplace_meta()

        assert meta is not None
        assert meta.name == "test-marketplace"
        assert meta.display_name == "Test Marketplace"

    def test_get_plugins_list_empty(self, temp_repo):
        """Test getting empty plugins list."""
        reader = GitRepoReader(temp_repo)
        plugins = reader.get_plugins_list()

        assert plugins == []

    def test_get_pending_submissions_empty(self, temp_repo):
        """Test getting empty submissions list."""
        reader = GitRepoReader(temp_repo)
        submissions = reader.get_pending_submissions()

        assert submissions == []


class TestGitRepoWriter:
    """Tests for GitRepoWriter."""

    def test_create_submission(self, temp_repo):
        """Test creating a submission."""
        writer = GitRepoWriter(temp_repo)

        plugin = PluginMetadata(
            name="test-plugin",
            description="Test Description",
            version="1.0.0",
            author=Author(name="Test Author", email="author@test.com")
        )
        submitter = SubmitterInfo(
            name="Submitter",
            email="submitter@test.com",
            submitted_at="2026-04-14T10:00:00Z",
            message="Test submission"
        )
        review_status = ReviewStatus(submission_id="test-001")

        submission = Submission(
            submission_id="test-001",
            plugin=plugin,
            submitter=submitter,
            review_status=review_status
        )

        result = writer.create_submission(submission)
        assert result is True

        # Verify files exist
        submission_dir = temp_repo / "pending" / "submissions" / "test-001"
        assert submission_dir.exists()
        assert (submission_dir / "plugin.json").exists()
        assert (submission_dir / "submitter.json").exists()

    def test_approve_submission(self, temp_repo):
        """Test approving a submission."""
        writer = GitRepoWriter(temp_repo)

        # First create a submission
        plugin = PluginMetadata(
            name="approved-plugin",
            description="Approved Plugin",
            version="1.0.0",
            author=Author(name="Author", email="author@test.com")
        )
        submitter = SubmitterInfo(
            name="Submitter",
            email="submitter@test.com",
            submitted_at="2026-04-14T10:00:00Z"
        )
        submission = Submission(
            submission_id="approve-001",
            plugin=plugin,
            submitter=submitter,
            review_status=ReviewStatus(submission_id="approve-001")
        )
        writer.create_submission(submission)

        # Approve it
        result = writer.approve_submission(
            "approve-001",
            "admin@test.com",
            "Looks good"
        )
        assert result is True

        # Verify plugin created
        plugin_dir = temp_repo / "plugins" / "approved-plugin"
        assert plugin_dir.exists()

    def test_add_rating(self, temp_repo):
        """Test adding a rating."""
        # First create a plugin
        writer = GitRepoWriter(temp_repo)

        plugin = PluginMetadata(
            name="rated-plugin",
            description="Rated Plugin",
            version="1.0.0",
            author=Author(name="Author", email="author@test.com")
        )
        submitter = SubmitterInfo(
            name="Submitter",
            email="submitter@test.com",
            submitted_at="2026-04-14T10:00:00Z"
        )
        submission = Submission(
            submission_id="rate-001",
            plugin=plugin,
            submitter=submitter,
            review_status=ReviewStatus(submission_id="rate-001")
        )
        writer.create_submission(submission)
        writer.approve_submission("rate-001", "admin@test.com", "ok")

        # Add rating
        rating = Rating(
            user="user@test.com",
            rating=5,
            comment="Great!",
            rated_at="2026-04-14T12:00:00Z"
        )
        result = writer.add_rating("rated-plugin", rating)
        assert result is True

        # Verify rating
        reader = GitRepoReader(temp_repo)
        ratings = reader.get_ratings("rated-plugin")
        assert ratings is not None
        assert ratings.total_ratings == 1
        assert ratings.average_rating == 5.0