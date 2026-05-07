"""Plugin API endpoints."""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import (
    Plugin, PluginWithSource, RatingSubmit, Rating,
)

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@router.get("/", response_model=List[PluginWithSource])
async def list_plugins(
    search: Optional[str] = Query(None, description="Search keyword"),
    keyword: Optional[str] = Query(None, description="Filter by keyword")
):
    """Get list of all plugins with source info."""
    reader = GitRepoReader()
    plugins = reader.get_plugins_list()
    result = []
    for name in plugins:
        p = reader.get_plugin_with_source(name)
        if p:
            result.append(p)

    # Apply filters
    if search:
        result = [p for p in result
                  if search.lower() in p.name.lower()
                  or search.lower() in p.description.lower()]

    if keyword:
        result = [p for p in result if keyword in p.keywords]

    return result


@router.get("/{name}", response_model=PluginWithSource)
async def get_plugin(name: str):
    """Get a specific plugin by name with source info."""
    reader = GitRepoReader()
    plugin = reader.get_plugin_with_source(name)

    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")

    return plugin


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