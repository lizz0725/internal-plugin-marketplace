"""Git repository operations for reading and writing plugin data."""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess

from app.config import settings
from app.models import (
    PluginMetadata, Plugin, PluginWithSource,
    MarketplaceMeta, SourceInfo,
    PluginRatings, Rating,
)


class GitRepoReader:
    """Read data from the Git plugin repository."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or settings.plugins_repo_path
        self._cache: Dict[str, Any] = {}

    def _read_json(self, file_path: Path) -> Optional[dict]:
        """Read a JSON file from the repository."""
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_marketplace_meta(self) -> Optional[MarketplaceMeta]:
        """Get marketplace metadata."""
        data = self._read_json(self.repo_path / "marketplace.json")
        if data:
            return MarketplaceMeta(**data)
        return None

    def get_plugins_list(self) -> List[str]:
        """Get list of all plugin names."""
        plugins_dir = self.repo_path / "plugins"
        if not plugins_dir.exists():
            return []
        return [d.name for d in plugins_dir.iterdir() if d.is_dir()]

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a specific plugin's information."""
        plugin_dir = self.repo_path / "plugins" / name
        if not plugin_dir.exists():
            return None

        # Read plugin.json
        plugin_json = self._read_json(plugin_dir / ".claude-plugin" / "plugin.json")
        if not plugin_json:
            return None

        metadata = PluginMetadata(**plugin_json)

        # Read versions.json
        versions_json = self._read_json(plugin_dir / ".claude-plugin" / "versions.json")
        versions = Versions(**versions_json) if versions_json else None

        # Read ratings
        ratings = self.get_ratings(name)

        return Plugin(
            name=metadata.name,
            description=metadata.description,
            version=metadata.version,
            author=metadata.author,
            keywords=metadata.keywords,
            license=metadata.license,
            homepage=metadata.homepage,
            average_rating=ratings.average_rating if ratings else 0.0,
            total_ratings=ratings.total_ratings if ratings else 0,
            versions=versions
        )

    def get_all_plugins(self) -> List[Plugin]:
        """Get all plugins."""
        return [p for name in self.get_plugins_list()
                if (p := self.get_plugin(name)) is not None]

    def get_sources(self) -> Optional[dict]:
        """Read sources.json for upstream tracking info."""
        return self._read_json(self.repo_path / "sources.json")

    def get_plugin_with_source(self, name: str) -> Optional[PluginWithSource]:
        """Get plugin info with source tracking."""
        plugin = self.get_plugin(name)
        if not plugin:
            return None

        sources = self.get_sources()
        source_info = None
        stars = 0
        homepage = None
        tags = []

        if sources:
            for entry in sources.get("plugins", []):
                if entry["name"] == name:
                    src = entry.get("source", {})
                    source_info = SourceInfo(**src) if src else None
                    stars = entry.get("stars", 0)
                    homepage = entry.get("homepage")
                    tags = entry.get("tags", [])
                    break

        return PluginWithSource(
            **plugin.model_dump(),
            source=source_info,
            stars=stars,
            homepage=homepage,
            tags=tags
        )

    def get_ratings(self, plugin_name: str) -> Optional[PluginRatings]:
        """Get ratings for a plugin."""
        data = self._read_json(self.repo_path / "ratings" / f"{plugin_name}.json")
        if data:
            return PluginRatings(**data)
        return None


class GitRepoWriter:
    """Write data to the Git plugin repository."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or settings.plugins_repo_path

    def _write_json(self, file_path: Path, data: dict) -> None:
        """Write data to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _run_git(self, *args: str) -> bool:
        """Run a git command in the repository."""
        try:
            subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def add_rating(self, plugin_name: str, rating: Rating) -> bool:
        """Add a rating to a plugin."""
        ratings_file = self.repo_path / "ratings" / f"{plugin_name}.json"

        reader = GitRepoReader(self.repo_path)
        existing = reader.get_ratings(plugin_name)

        if existing:
            # Check if user already rated
            for r in existing.ratings:
                if r.user == rating.user:
                    # Update existing rating
                    r.rating = rating.rating
                    r.comment = rating.comment
                    r.rated_at = rating.rated_at
                    break
            else:
                existing.ratings.append(rating)

            # Recalculate average
            total = sum(r.rating for r in existing.ratings)
            existing.average_rating = total / len(existing.ratings)
            existing.total_ratings = len(existing.ratings)
        else:
            existing = PluginRatings(
                plugin=plugin_name,
                average_rating=rating.rating,
                total_ratings=1,
                ratings=[rating]
            )

        self._write_json(ratings_file, existing.model_dump())
        return True

    def commit_changes(self, message: str) -> bool:
        """Commit all changes to the repository."""
        self._run_git("add", "-A")
        self._run_git("commit", "-m", message)
        return True

    def create_tag(self, tag_name: str) -> bool:
        """Create a git tag."""
        return self._run_git("tag", tag_name)

    def push_to_remote(self, remotes: List[dict]) -> bool:
        """Push commits and tags to all configured remotes."""
        ok = True
        for remote in remotes:
            name = remote.get("name", "origin")
            url = remote.get("url", "")
            branch = remote.get("push_branch", "master")
            if url:
                self._run_git("remote", "add", name, url)
                self._run_git("remote", "set-url", name, url)
            ok &= self._run_git("push", name, branch)
            self._run_git("push", name, "--tags")
        return ok