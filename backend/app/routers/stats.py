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
    sources = reader.get_sources()

    plugins_count = len(plugins)
    total_ratings = sum(p.total_ratings for p in plugins)

    # Sync stats from sources.json
    sync_stats = {"synced": 0, "pending": 0, "failed": 0}
    if sources:
        for entry in sources.get("plugins", []):
            status = entry.get("source", {}).get("last_sync_status", "")
            if status == "success":
                sync_stats["synced"] += 1
            elif status == "failed":
                sync_stats["failed"] += 1
            else:
                sync_stats["pending"] += 1

    return {
        "plugins_count": plugins_count,
        "total_ratings": total_ratings,
        "marketplace_name": meta.display_name if meta else "Plugin Marketplace",
        "sync": sync_stats,
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
