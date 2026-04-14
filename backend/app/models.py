"""Pydantic data models for the plugin marketplace."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class Author(BaseModel):
    """Plugin author information."""
    name: str
    email: EmailStr


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


class SubmitterInfo(BaseModel):
    """Plugin submission submitter information."""
    name: str
    email: EmailStr
    department: Optional[str] = None
    submitted_at: str
    message: Optional[str] = None


class ReviewStatus(BaseModel):
    """Review status for a submission."""
    submission_id: str
    status: str = "pending"  # pending, approved, rejected
    reviewed_by: Optional[EmailStr] = None
    reviewed_at: Optional[str] = None
    review_notes: Optional[str] = None


class Submission(BaseModel):
    """A plugin submission for review."""
    submission_id: str
    plugin: PluginMetadata
    submitter: SubmitterInfo
    review_status: ReviewStatus
    auto_check_results: Optional[dict] = None


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


class PluginSubmit(BaseModel):
    """Request body for submitting a new plugin."""
    plugin: PluginMetadata
    submitter: SubmitterInfo
    files: Optional[dict] = None  # 文件内容或路径


class MarketplaceMeta(BaseModel):
    """Marketplace metadata."""
    name: str
    display_name: str
    description: str
    owner: Author
    repository: Optional[str] = None
    created_at: str
    plugins_count: int = 0