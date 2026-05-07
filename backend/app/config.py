"""Application configuration management."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    # Plugin repository path (local directory)
    plugins_repo_path: Path = Path(os.getenv("PLUGINS_REPO_PATH", "../plugins-repo"))

    # Remote Git repository URL (for client installation)
    # Example: https://github.com/username/cc-plugin-marketplace.git
    plugins_repo_url: str = ""

    # Marketplace name (displayed in frontend)
    marketplace_name: str = "内部插件市场"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Admin emails (comma-separated)
    admin_emails: str = ""

    # File upload limits
    max_upload_size_mb: int = 50
    max_extracted_files: int = 500
    max_extracted_size_mb: int = 200

    # Git sync limits
    git_clone_timeout_seconds: int = 60
    max_clone_size_mb: int = 200

    # Git proxy for cloning (auto-detected from environment if not set)
    # Example: http://127.0.0.1:7890
    git_proxy: str = ""

    @property
    def effective_git_proxy(self) -> str:
        """Return git proxy, falling back to common env vars."""
        if self.git_proxy:
            return self.git_proxy
        return (
            os.environ.get("HTTPS_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTP_PROXY")
            or os.environ.get("http_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("all_proxy")
            or ""
        )

    # Temp directory for processing
    temp_processing_dir: str = "/tmp/plugin-marketplace"


settings = Settings()