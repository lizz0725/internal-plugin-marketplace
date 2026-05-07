"""Tests for file_service module."""
import json
import zipfile
import pytest
from pathlib import Path
import tempfile

from app.services.file_service import (
    PluginStructureValidator,
    ZipProcessor,
    GitSyncProcessor,
)


SAMPLE_PLUGIN_JSON = {
    "name": "test-plugin",
    "description": "A test plugin",
    "version": "1.0.0",
    "author": {"name": "Tester", "email": "tester@test.com"},
    "keywords": ["test"],
    "license": "proprietary",
}


class TestPluginStructureValidator:
    def test_valid_structure(self, tmp_path):
        """Should validate a correct .claude-plugin directory."""
        plugin_dir = tmp_path / "test-plugin"
        claude_dir = plugin_dir / ".claude-plugin"
        claude_dir.mkdir(parents=True)

        with open(claude_dir / "plugin.json", "w") as f:
            json.dump(SAMPLE_PLUGIN_JSON, f)

        metadata = PluginStructureValidator.validate(plugin_dir)
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"

    def test_missing_claude_plugin_dir(self, tmp_path):
        """Should fail when .claude-plugin/ is missing."""
        empty_dir = tmp_path / "empty-dir"
        empty_dir.mkdir()
        with pytest.raises(ValueError, match="Missing .claude-plugin/"):
            PluginStructureValidator.validate(empty_dir)

    def test_missing_plugin_json(self, tmp_path):
        """Should fail when plugin.json is missing."""
        claude_dir = tmp_path / "test" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        with pytest.raises(ValueError, match="Missing"):
            PluginStructureValidator.validate(claude_dir.parent)

    def test_invalid_plugin_json(self, tmp_path):
        """Should fail when plugin.json is malformed."""
        claude_dir = tmp_path / "test" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        with open(claude_dir / "plugin.json", "w") as f:
            f.write("not json")
        with pytest.raises(ValueError, match="Invalid plugin.json"):
            PluginStructureValidator.validate(claude_dir.parent)

    def test_invalid_plugin_name(self, tmp_path):
        """Should fail when plugin name has invalid characters."""
        claude_dir = tmp_path / "test" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        data = dict(SAMPLE_PLUGIN_JSON, name="invalid name with spaces!")
        with open(claude_dir / "plugin.json", "w") as f:
            json.dump(data, f)
        with pytest.raises(ValueError, match="Invalid plugin name"):
            PluginStructureValidator.validate(claude_dir.parent)

    def test_unexpected_subdirectory(self, tmp_path):
        """Should fail when unexpected subdirectories exist."""
        claude_dir = tmp_path / "test" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        (claude_dir / "unexpected").mkdir()
        with open(claude_dir / "plugin.json", "w") as f:
            json.dump(SAMPLE_PLUGIN_JSON, f)
        with pytest.raises(ValueError, match="Unexpected directory"):
            PluginStructureValidator.validate(claude_dir.parent)

    def test_allowed_subdirectories(self, tmp_path):
        """Should accept commands/, hooks/, assets/ subdirectories."""
        claude_dir = tmp_path / "test" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        (claude_dir / "commands").mkdir()
        (claude_dir / "hooks").mkdir()
        (claude_dir / "assets").mkdir()
        with open(claude_dir / "plugin.json", "w") as f:
            json.dump(SAMPLE_PLUGIN_JSON, f)
        metadata = PluginStructureValidator.validate(claude_dir.parent)
        assert metadata.name == "test-plugin"


class TestZipProcessor:
    def test_valid_plugin_zip(self, tmp_path):
        """Should extract and validate a valid plugin zip."""
        # Create source plugin
        source = tmp_path / "source"
        claude_dir = source / "test-plugin" / ".claude-plugin"
        claude_dir.mkdir(parents=True)
        with open(claude_dir / "plugin.json", "w") as f:
            json.dump(SAMPLE_PLUGIN_JSON, f)

        # Create zip
        zip_path = tmp_path / "plugin.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for file in claude_dir.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(source / "test-plugin"))

        dest = tmp_path / "dest"
        dest.mkdir()
        metadata = ZipProcessor.extract_and_validate(zip_path, dest)
        assert metadata.name == "test-plugin"
        assert (dest / ".claude-plugin" / "plugin.json").exists()

    def test_no_claude_plugin_in_zip(self, tmp_path):
        """Should fail when zip has no .claude-plugin/ directory."""
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("some-file.txt", "content")

        dest = tmp_path / "dest"
        dest.mkdir()
        with pytest.raises(ValueError, match="No .claude-plugin/ directory found"):
            ZipProcessor.extract_and_validate(zip_path, dest)

    def test_zip_bomb_detection(self, tmp_path):
        """Should detect zip bombs via compression ratio."""
        zip_path = tmp_path / "bomb.zip"
        # A file that compresses very well (high ratio)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            large_content = b"A" * 1_000_000  # 1MB uncompressed
            zf.writestr("large-file.txt", large_content)

        dest = tmp_path / "dest"
        dest.mkdir()
        with pytest.raises(ValueError, match="Suspicious compression ratio"):
            ZipProcessor.extract_and_validate(zip_path, dest)


class TestGitSyncProcessor:
    def test_invalid_url_format(self, tmp_path):
        """Should reject invalid Git URL formats."""
        dest = tmp_path / "dest"
        dest.mkdir()
        with pytest.raises(ValueError, match="Invalid Git URL format"):
            GitSyncProcessor.clone_and_validate("ftp://bad-url.com/repo", dest)

    def test_build_auth_url(self):
        """Should inject token into HTTPS URL correctly."""
        url = "https://github.com/user/repo.git"
        token = "ghp_test123"
        result = GitSyncProcessor._build_auth_url(url, token)
        assert result == "https://ghp_test123@github.com/user/repo.git"
