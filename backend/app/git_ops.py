"""Git repository operations for reading and writing plugin data."""
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import subprocess

from app.config import settings
from app.models import (
    PluginMetadata, Plugin, PluginWithSource,
    MarketplaceMeta, SourceInfo,
    Versions, VersionInfo, PluginRatings, Rating,
    Submission, SubmitterInfo, ReviewStatus, SubmissionTypeInfo
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

    def get_pending_submissions(self) -> List[Submission]:
        """Get all pending submissions."""
        submissions_dir = self.repo_path / "pending" / "submissions"
        if not submissions_dir.exists():
            return []

        submissions = []
        for submission_dir in submissions_dir.iterdir():
            if not submission_dir.is_dir():
                continue

            plugin_json = self._read_json(submission_dir / "plugin.json")
            submitter_json = self._read_json(submission_dir / "submitter.json")
            review_json = self._read_json(submission_dir / "review_status.json")

            if plugin_json and submitter_json:
                submission = Submission(
                    submission_id=submission_dir.name,
                    plugin=PluginMetadata(**plugin_json),
                    submitter=SubmitterInfo(**submitter_json),
                    review_status=ReviewStatus(**(review_json or {"submission_id": submission_dir.name}))
                )
                submissions.append(submission)

        return submissions

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        """Get a specific submission."""
        submission_dir = self.repo_path / "pending" / "submissions" / submission_id
        if not submission_dir.exists():
            return None

        plugin_json = self._read_json(submission_dir / "plugin.json")
        submitter_json = self._read_json(submission_dir / "submitter.json")
        review_json = self._read_json(submission_dir / "review_status.json")

        if not plugin_json or not submitter_json:
            return None

        return Submission(
            submission_id=submission_id,
            plugin=PluginMetadata(**plugin_json),
            submitter=SubmitterInfo(**submitter_json),
            review_status=ReviewStatus(**(review_json or {"submission_id": submission_id}))
        )


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

    def create_submission(self, submission: Submission) -> bool:
        """Create a new submission directory."""
        submission_dir = self.repo_path / "pending" / "submissions" / submission.submission_id
        submission_dir.mkdir(parents=True, exist_ok=True)

        # Write files
        self._write_json(
            submission_dir / "plugin.json",
            submission.plugin.model_dump()
        )
        self._write_json(
            submission_dir / "submitter.json",
            submission.submitter.model_dump()
        )
        self._write_json(
            submission_dir / "review_status.json",
            submission.review_status.model_dump()
        )

        return True

    def create_file_based_submission(
        self,
        submission_id: str,
        plugin: PluginMetadata,
        submitter: SubmitterInfo,
        source_dir: Path,
        submission_type: SubmissionTypeInfo,
    ) -> bool:
        """Create a submission with uploaded/synced plugin files."""
        submission_dir = self.repo_path / "pending" / "submissions" / submission_id
        submission_dir.mkdir(parents=True, exist_ok=True)

        # Write metadata files
        self._write_json(
            submission_dir / "plugin.json",
            plugin.model_dump()
        )
        self._write_json(
            submission_dir / "submitter.json",
            submitter.model_dump()
        )
        self._write_json(
            submission_dir / "review_status.json",
            {"submission_id": submission_id, "status": "pending"}
        )
        self._write_json(
            submission_dir / "submission_type.json",
            submission_type.model_dump()
        )

        # Copy plugin files
        files_dir = submission_dir / "files"
        shutil.copytree(source_dir, files_dir, dirs_exist_ok=True)

        return True

    def approve_submission(self, submission_id: str, reviewer_email: str, notes: str) -> bool:
        """Approve a submission and move it to plugins."""
        submission_dir = self.repo_path / "pending" / "submissions" / submission_id
        if not submission_dir.exists():
            return False

        # Read submission data
        reader = GitRepoReader(self.repo_path)
        submission = reader.get_submission(submission_id)
        if not submission:
            return False

        # Check if this is a file-based submission
        type_file = submission_dir / "submission_type.json"
        is_file_based = type_file.exists()

        plugin_name = submission.plugin.name
        plugin_dir = self.repo_path / "plugins" / plugin_name
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir(parents=True, exist_ok=True)

        if is_file_based:
            # Copy files from submission to plugin directory
            src_files = submission_dir / "files"
            if src_files.exists():
                shutil.copytree(src_files, plugin_dir, dirs_exist_ok=True)
        else:
            # Write plugin.json from form data (existing behavior)
            self._write_json(
                claude_plugin_dir / "plugin.json",
                submission.plugin.model_dump(exclude_none=True)
            )

        # Write versions.json (initial version)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        version_tag = f"{plugin_name}-v{submission.plugin.version}"
        versions = Versions(
            current=submission.plugin.version,
            versions=[
                VersionInfo(
                    version=submission.plugin.version,
                    released_at=now,
                    git_ref=version_tag,
                    changelog="初始版本",
                    status="current"
                )
            ]
        )
        self._write_json(claude_plugin_dir / "versions.json", versions.model_dump())

        # Create initial ratings file
        self._write_json(
            self.repo_path / "ratings" / f"{plugin_name}.json",
            {"plugin": plugin_name, "average_rating": 0.0, "total_ratings": 0, "ratings": []}
        )

        # Update review status
        review_status = ReviewStatus(
            submission_id=submission_id,
            status="approved",
            reviewed_by=reviewer_email,
            reviewed_at=datetime.now(timezone.utc).isoformat(),
            review_notes=notes
        )
        self._write_json(submission_dir / "review_status.json", review_status.model_dump())

        # Update marketplace.json
        meta = reader.get_marketplace_meta()
        if meta:
            meta.plugins_count = len(reader.get_plugins_list()) + 1
            self._write_json(self.repo_path / "marketplace.json", meta.model_dump())

        return True

    def reject_submission(self, submission_id: str, reviewer_email: str, reason: str) -> bool:
        """Reject a submission."""
        submission_dir = self.repo_path / "pending" / "submissions" / submission_id
        if not submission_dir.exists():
            return False

        review_status = ReviewStatus(
            submission_id=submission_id,
            status="rejected",
            reviewed_by=reviewer_email,
            reviewed_at=datetime.now(timezone.utc).isoformat(),
            review_notes=reason
        )
        self._write_json(submission_dir / "review_status.json", review_status.model_dump())

        return True

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

    def push_to_remote(self, remotes: Optional[List[dict]] = None) -> bool:
        """Push commits and tags to remote(s).

        Args:
            remotes: List of remote configs from sources.json.
                     Falls back to 'origin' if not provided.
        """
        if remotes:
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

        # Fallback to single 'origin'
        result = subprocess.run(
            ["git", "remote"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if "origin" not in result.stdout:
            return False
        push_ok = self._run_git("push", "origin", "master")
        if not push_ok:
            return False
        tags_ok = self._run_git("push", "origin", "--tags")
        return tags_ok