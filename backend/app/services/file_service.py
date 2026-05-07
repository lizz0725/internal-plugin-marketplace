"""File processing services for plugin submission (zip upload, git sync)."""
import json
import os
import zipfile
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models import PluginMetadata


class PluginStructureValidator:
    """Validate a .claude-plugin directory structure."""

    ALLOWED_SUBDIRS = {"commands", "hooks", "assets"}
    ALLOWED_SCRIPT_EXTENSIONS = {".sh", ".py", ".js", ".ts", ".bash", ".zsh"}

    @classmethod
    def validate(cls, plugin_dir: Path) -> PluginMetadata:
        """
        Validate a .claude-plugin directory and return parsed metadata.

        Expected structure:
            .claude-plugin/
            ├── plugin.json          (required)
            ├── commands/            (optional - slash command scripts)
            ├── hooks/               (optional - lifecycle hooks)
            └── assets/              (optional - resource files)

        Returns:
            PluginMetadata parsed from plugin.json
        """
        if not plugin_dir.is_dir():
            raise ValueError(f"Not a directory: {plugin_dir}")

        claude_plugin_dir = plugin_dir / ".claude-plugin"
        if not claude_plugin_dir.is_dir():
            raise ValueError(
                f"Missing .claude-plugin/ directory in {plugin_dir}"
            )

        # Read and parse plugin.json
        plugin_json_path = claude_plugin_dir / "plugin.json"
        if not plugin_json_path.exists():
            raise ValueError(f"Missing .claude-plugin/plugin.json in {plugin_dir}")

        try:
            with open(plugin_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            metadata = PluginMetadata(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid plugin.json: {e}")
        except Exception as e:
            raise ValueError(f"plugin.json validation failed: {e}")

        # Validate plugin name (alphanumeric + hyphens, no spaces)
        if not metadata.name or not metadata.name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Invalid plugin name: '{metadata.name}'. Use letters, numbers, hyphens, underscores.")

        # Validate subdirectory structure
        cls._validate_subdirs(claude_plugin_dir)

        # Check for path traversal attempts or dangerous files
        cls._check_security(claude_plugin_dir)

        return metadata

    @classmethod
    def _validate_subdirs(cls, claude_plugin_dir: Path) -> None:
        """Validate that only allowed subdirectories exist."""
        for item in claude_plugin_dir.iterdir():
            if item.is_dir() and item.name not in cls.ALLOWED_SUBDIRS:
                raise ValueError(
                    f"Unexpected directory '{item.name}' in .claude-plugin/. "
                    f"Allowed: {', '.join(sorted(cls.ALLOWED_SUBDIRS))}"
                )

    @classmethod
    def _check_security(cls, claude_plugin_dir: Path) -> None:
        """Check for security issues: symlinks outside tree, etc."""
        for f in claude_plugin_dir.rglob("*"):
            if f.is_symlink():
                target = f.resolve()
                if not str(target).startswith(str(claude_plugin_dir.resolve())):
                    raise ValueError(
                        f"Symlink '{f}' points outside the plugin directory: {target}"
                    )


class ZipProcessor:
    """Process zip file uploads for plugin submission."""

    @staticmethod
    def extract_and_validate(zip_path: Path, dest_dir: Path) -> PluginMetadata:
        """
        Extract a zip file and validate the plugin structure.

        The zip should contain a .claude-plugin/ directory at its root
        (or be a single directory containing .claude-plugin/).

        Returns:
            PluginMetadata parsed from the extracted plugin
        """
        if not zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")

        # Validate zip safety before extraction
        ZipProcessor._check_zip_safety(zip_path)

        # Extract to temp directory first
        with tempfile.TemporaryDirectory() as tmp:
            extract_root = Path(tmp) / "extracted"
            extract_root.mkdir(parents=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                # Check for path traversal in zip entries
                for name in zf.namelist():
                    resolved = (extract_root / name).resolve()
                    if not str(resolved).startswith(str(extract_root.resolve())):
                        raise ValueError(f"Path traversal detected in zip: {name}")

                zf.extractall(extract_root)

            # Find .claude-plugin directory
            claude_dir = ZipProcessor._find_claude_plugin_dir(extract_root)
            if claude_dir is None:
                raise ValueError(
                    "No .claude-plugin/ directory found in zip. "
                    "The zip must contain a .claude-plugin/ directory."
                )

            # Validate structure and get metadata
            metadata = PluginStructureValidator.validate(claude_dir.parent)

            # Copy only .claude-plugin/ directory to destination
            shutil.copytree(claude_dir, dest_dir / ".claude-plugin", dirs_exist_ok=True)

        return metadata

    @staticmethod
    def _check_zip_safety(zip_path: Path) -> None:
        """Validate zip file is safe to extract (prevent zip bombs)."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            info_list = zf.infolist()

            # Check total entry count
            if len(info_list) > settings.max_extracted_files:
                raise ValueError(
                    f"Zip contains {len(info_list)} files, "
                    f"exceeds limit of {settings.max_extracted_files}"
                )

            # Check total uncompressed size
            total_uncompressed = sum(fi.file_size for fi in info_list)
            max_bytes = settings.max_extracted_size_mb * 1024 * 1024
            if total_uncompressed > max_bytes:
                raise ValueError(
                    f"Zip uncompressed size ({total_uncompressed / 1024 / 1024:.1f} MB) "
                    f"exceeds limit of {settings.max_extracted_size_mb} MB"
                )

            # Check compression ratio (zip bomb detection)
            total_compressed = sum(fi.compress_size for fi in info_list)
            if total_compressed > 0:
                ratio = total_uncompressed / total_compressed
                if ratio > 100:
                    raise ValueError(
                        f"Suspicious compression ratio ({ratio:.0f}:1). "
                        f"File may be a zip bomb."
                    )

    @staticmethod
    def _find_claude_plugin_dir(search_dir: Path) -> Optional[Path]:
        """Find .claude-plugin/ directory within an extracted zip."""
        # Direct child
        candidate = search_dir / ".claude-plugin"
        if candidate.is_dir():
            return candidate

        # Single subdirectory wrapper (e.g., plugin-name/.claude-plugin/)
        children = [d for d in search_dir.iterdir() if d.is_dir()]
        if len(children) == 1:
            candidate = children[0] / ".claude-plugin"
            if candidate.is_dir():
                return candidate

        return None


class GitSyncProcessor:
    """Process git repository sync for plugin submission."""

    @staticmethod
    def clone_and_validate(
        git_url: str,
        dest_dir: Path,
        ref: str = "main",
        token: Optional[str] = None,
    ) -> PluginMetadata:
        """
        Clone a git repository, extract plugin files, and validate.

        Args:
            git_url: Remote git repository URL
            dest_dir: Destination directory for plugin files
            ref: Branch, tag, or commit SHA to checkout
            token: Optional access token for private repos

        Returns:
            PluginMetadata parsed from the cloned plugin
        """
        # Validate URL format
        if not git_url.startswith(("https://", "http://", "git@", "ssh://")):
            raise ValueError(f"Invalid Git URL format: {git_url}")

        # Build authenticated URL if token provided
        clone_url = git_url
        if token and git_url.startswith("https://"):
            clone_url = GitSyncProcessor._build_auth_url(git_url, token)

        # Create temp directory for cloning
        with tempfile.TemporaryDirectory() as tmp:
            clone_dir = Path(tmp) / "repo"
            clone_dir.mkdir(parents=True)

            # Use proxy from settings (falls back to env vars)
            proxy_url = settings.effective_git_proxy

            # Build git clone command (with proxy if set)
            if proxy_url:
                git_cmd = [
                    "git", "-c", f"http.proxy={proxy_url}",
                    "-c", f"https.proxy={proxy_url}",
                    "clone", "--depth", "1", clone_url, str(clone_dir),
                ]
            else:
                git_cmd = ["git", "clone", "--depth", "1", clone_url, str(clone_dir)]

            # Shallow clone
            try:
                subprocess.run(
                    git_cmd,
                    capture_output=True,
                    text=True,
                    timeout=settings.git_clone_timeout_seconds,
                    check=True,
                )
            except subprocess.TimeoutExpired:
                raise ValueError(
                    f"Git clone timed out after {settings.git_clone_timeout_seconds}s"
                )
            except subprocess.CalledProcessError as e:
                proxy_hint = ""
                if not proxy_url:
                    proxy_hint = (
                        ". No proxy detected. If you need a proxy, "
                        "set GIT_PROXY=http://127.0.0.1:7890 in backend/.env "
                        "or set HTTPS_PROXY environment variable"
                    )
                else:
                    proxy_hint = f" (proxy: {proxy_url})"
                raise ValueError(
                    f"Git clone failed: {e.stderr.strip() or 'unknown error'}{proxy_hint}"
                )

            # Checkout specific ref if different from default
            if ref != "main":
                try:
                    subprocess.run(
                        ["git", "checkout", ref],
                        cwd=clone_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    raise ValueError(
                        f"Failed to checkout ref '{ref}': {e.stderr.strip()}"
                    )

            # Check total repo size
            GitSyncProcessor._check_repo_size(clone_dir)

            # Find .claude-plugin directory
            claude_dir = GitSyncProcessor._find_claude_plugin_dir(clone_dir)
            if claude_dir is None:
                raise ValueError(
                    "No .claude-plugin/ directory found in repository. "
                    "The repository must contain a .claude-plugin/ directory."
                )

            # Validate structure and get metadata
            metadata = PluginStructureValidator.validate(claude_dir.parent)

            # Copy only .claude-plugin/ directory to destination (not the entire repo)
            shutil.copytree(claude_dir, dest_dir / ".claude-plugin", dirs_exist_ok=True)

        return metadata

    @staticmethod
    def _build_auth_url(url: str, token: str) -> str:
        """Inject token into Git URL for authentication."""
        # https://github.com/user/repo.git -> https://token@github.com/user/repo.git
        prefix = "https://"
        if url.startswith(prefix):
            return f"{prefix}{token}@{url[len(prefix):]}"
        return url

    @staticmethod
    def _check_repo_size(repo_dir: Path) -> None:
        """Check that cloned repository size is within limits."""
        total_size = sum(
            f.stat().st_size for f in repo_dir.rglob("*") if f.is_file()
        )
        max_bytes = settings.max_clone_size_mb * 1024 * 1024
        if total_size > max_bytes:
            raise ValueError(
                f"Repository size ({total_size / 1024 / 1024:.1f} MB) "
                f"exceeds limit of {settings.max_clone_size_mb} MB"
            )

    @staticmethod
    def _find_claude_plugin_dir(search_dir: Path) -> Optional[Path]:
        """Find .claude-plugin/ directory in the cloned repo."""
        candidate = search_dir / ".claude-plugin"
        if candidate.is_dir():
            return candidate

        # Single subdirectory wrapper
        children = [d for d in search_dir.iterdir() if d.is_dir() and not d.name.startswith(".git")]
        if len(children) == 1:
            candidate = children[0] / ".claude-plugin"
            if candidate.is_dir():
                return candidate

        return None
