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
    plugins_repo_url: str = ""

    # Marketplace name (displayed in frontend)
    marketplace_name: str = "插件聚合市场"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Admin emails (comma-separated)
    admin_emails: str = ""


settings = Settings()