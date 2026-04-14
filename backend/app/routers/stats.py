"""Statistics API endpoints."""
from fastapi import APIRouter

from app.git_ops import GitRepoReader

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def get_stats_overview():
    """Get marketplace statistics overview."""
    reader = GitRepoReader()

    meta = reader.get_marketplace_meta()
    plugins = reader.get_all_plugins()
    submissions = reader.get_pending_submissions()

    pending_count = len([s for s in submissions if s.review_status.status == "pending"])

    # Calculate total ratings
    total_ratings = sum(p.total_ratings for p in plugins)

    return {
        "plugins_count": meta.plugins_count if meta else len(plugins),
        "pending_reviews": pending_count,
        "total_ratings": total_ratings,
        "marketplace_name": meta.display_name if meta else "Unknown"
    }


@router.get("/ratings")
async def get_ratings_stats():
    """Get ratings distribution statistics."""
    reader = GitRepoReader()
    plugins = reader.get_all_plugins()

    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for plugin in plugins:
        ratings = reader.get_ratings(plugin.name)
        if ratings:
            for r in ratings.ratings:
                distribution[r.rating] = distribution.get(r.rating, 0) + 1

    return {"distribution": distribution}