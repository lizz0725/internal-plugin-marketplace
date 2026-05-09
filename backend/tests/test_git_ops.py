"""Tests for git_ops module."""
import pytest
from pathlib import Path
import tempfile
import shutil
import json

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import PluginMetadata, Author, Rating


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / "test-repo"

    # Create structure
    repo_path.mkdir()
    (repo_path / "plugins").mkdir()
    (repo_path / "ratings").mkdir()

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

    def test_get_sources_none(self, temp_repo):
        """Test get_sources returns None when no sources.json."""
        reader = GitRepoReader(temp_repo)
        sources = reader.get_sources()
        assert sources is None


class TestGitRepoWriter:
    """Tests for GitRepoWriter."""

    def test_add_rating(self, temp_repo):
        """Test adding a rating."""
        writer = GitRepoWriter(temp_repo)

        # Manually create a plugin directory with plugin.json
        plugin_dir = temp_repo / "plugins" / "rated-plugin" / ".claude-plugin"
        plugin_dir.mkdir(parents=True)
        plugin_json = {
            "name": "rated-plugin",
            "description": "Rated Plugin",
            "version": "1.0.0",
            "author": {"name": "Author", "email": "author@test.com"}
        }
        with open(plugin_dir / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

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
