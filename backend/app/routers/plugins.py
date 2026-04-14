"""Plugin API endpoints."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import Plugin, PluginSubmit, RatingSubmit, Submission, ReviewStatus, Rating

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@router.get("/", response_model=List[Plugin])
async def list_plugins(
    search: Optional[str] = Query(None, description="Search keyword"),
    keyword: Optional[str] = Query(None, description="Filter by keyword")
):
    """Get list of all plugins."""
    reader = GitRepoReader()
    plugins = reader.get_all_plugins()

    # Apply filters
    if search:
        plugins = [p for p in plugins
                   if search.lower() in p.name.lower()
                   or search.lower() in p.description.lower()]

    if keyword:
        plugins = [p for p in plugins if keyword in p.keywords]

    return plugins


@router.get("/{name}", response_model=Plugin)
async def get_plugin(name: str):
    """Get a specific plugin by name."""
    reader = GitRepoReader()
    plugin = reader.get_plugin(name)

    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")

    return plugin


@router.post("/submit")
async def submit_plugin(submission: PluginSubmit):
    """Submit a new plugin for review."""
    reader = GitRepoReader()

    # Check if plugin already exists in approved plugins
    existing = reader.get_plugin(submission.plugin.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Plugin '{submission.plugin.name}' already exists"
        )

    # Check if there's already a pending submission with the same name
    pending_submissions = reader.get_pending_submissions()
    for ps in pending_submissions:
        if ps.plugin.name == submission.plugin.name and ps.review_status.status == "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Plugin '{submission.plugin.name}' already has a pending submission"
            )

    # Generate submission ID
    submission_id = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"

    # Create submission
    full_submission = Submission(
        submission_id=submission_id,
        plugin=submission.plugin,
        submitter=submission.submitter,
        review_status=ReviewStatus(submission_id=submission_id)
    )

    writer = GitRepoWriter()
    writer.create_submission(full_submission)
    writer.commit_changes(f"submission: {submission.plugin.name} submitted by {submission.submitter.email}")

    return {"submission_id": submission_id, "status": "pending"}


@router.post("/{name}/rate")
async def rate_plugin(name: str, rating: RatingSubmit):
    """Submit a rating for a plugin."""
    reader = GitRepoReader()
    plugin = reader.get_plugin(name)

    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")

    rating_obj = Rating(
        user=rating.user_email,
        rating=rating.rating,
        comment=rating.comment,
        rated_at=datetime.now(timezone.utc).isoformat()
    )

    writer = GitRepoWriter()
    writer.add_rating(name, rating_obj)
    writer.commit_changes(f"rating: {rating.user_email} rated {name}")

    # Re-read to get updated average
    updated_ratings = GitRepoReader().get_ratings(name)
    return {"status": "success", "average_rating": updated_ratings.average_rating if updated_ratings else rating.rating}