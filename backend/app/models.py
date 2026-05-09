"""Pydantic data models for the plugin marketplace."""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr


class Author(BaseModel):
    """Plugin author information."""
    name: str
    email: Optional[EmailStr] = None


class PluginMetadata(BaseModel):
    """Plugin metadata from plugin.json."""
    name: str
    description: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    author: Author
    keywords: List[str] = []
    license: str = "proprietary"
    homepage: Optional[str] = None


class VersionInfo(BaseModel):
    """Single version information."""
    version: str
    released_at: str
    git_ref: str
    changelog: Optional[str] = None
    status: str = "available"  # current, available, deprecated


class Versions(BaseModel):
    """Plugin version history."""
    current: str
    versions: List[VersionInfo]


class Plugin(BaseModel):
    """Full plugin information for API response."""
    name: str
    description: str
    version: str
    author: Author
    keywords: List[str] = []
    license: str = "proprietary"
    homepage: Optional[str] = None
    average_rating: float = 0.0
    total_ratings: int = 0
    versions: Optional[Versions] = None


class Rating(BaseModel):
    """User rating for a plugin."""
    user: EmailStr
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    rated_at: str


class PluginRatings(BaseModel):
    """All ratings for a plugin."""
    plugin: str
    average_rating: float
    total_ratings: int
    ratings: List[Rating]


class RatingSubmit(BaseModel):
    """Request body for submitting a rating."""
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    user_email: EmailStr


class MarketplaceMeta(BaseModel):
    """Marketplace metadata."""
    name: str
    display_name: str
    description: str
    owner: Author
    repository: Optional[str] = None
    created_at: str
    plugins_count: int = 0


# ──────────────────────────────────────────
# Models for upstream aggregation marketplace
# ──────────────────────────────────────────

class SourceInfo(BaseModel):
    """Upstream source tracking for a plugin."""
    type: Literal["manual", "github_single", "github_monorepo"]
    repo_url: Optional[str] = None
    repo_ref: Optional[str] = None
    commit_sha: Optional[str] = None
    subdir: Optional[str] = None
    version: Optional[str] = None
    last_sync_at: Optional[str] = None
    last_sync_status: Optional[str] = None  # pending, success, failed, unchanged


class SyncStatus(BaseModel):
    """Sync status for all plugins."""
    last_updated: Optional[str] = None
    total_plugins: int = 0
    synced: int = 0
    pending: int = 0
    failed: int = 0
    plugins: List[dict] = []


class PluginWithSource(Plugin):
    """Plugin info with source tracking."""
    source: Optional[SourceInfo] = None
    stars: int = 0
    homepage: Optional[str] = None
    tags: List[str] = []