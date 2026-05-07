"""FastAPI application entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.git_ops import GitRepoReader
from app.routers import plugins, stats

app = FastAPI(
    title="Plugin Marketplace",
    description="Claude Code 插件聚合市场",
    version="0.2.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(plugins.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Plugin Marketplace API", "version": "0.2.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/sync/status")
async def sync_status():
    """Get the sync status of all upstream plugins."""
    reader = GitRepoReader()
    sources = reader.get_sources()
    if not sources:
        return {"last_updated": None, "total_plugins": 0, "synced": 0, "pending": 0, "failed": 0, "plugins": []}

    plugins_list = sources.get("plugins", [])
    last_updated = sources.get("last_updated")

    stats_counts = {"synced": 0, "pending": 0, "failed": 0}
    plugin_statuses = []
    for entry in plugins_list:
        src = entry.get("source", {})
        status = src.get("last_sync_status", "unknown")
        plugin_statuses.append({
            "name": entry["name"],
            "display_name": entry.get("display_name", entry["name"]),
            "status": status,
            "type": src.get("type", "manual"),
            "stars": entry.get("stars", 0),
            "last_sync_at": src.get("last_sync_at"),
            "commit_sha": (src.get("commit_sha") or "")[:12] if src.get("commit_sha") else "",
        })

        if status == "success":
            stats_counts["synced"] += 1
        elif status == "failed":
            stats_counts["failed"] += 1
        else:
            stats_counts["pending"] += 1

    return {
        "last_updated": last_updated,
        "total_plugins": len(plugins_list),
        **stats_counts,
        "plugins": plugin_statuses,
    }


@app.post("/api/sync/trigger")
async def trigger_sync():
    """Trigger a manual sync run via the sync script."""
    import subprocess
    try:
        subprocess.Popen(
            ["python", "scripts/sync_plugins.py", "--no-push"],
            cwd=settings.plugins_repo_path.parent,
        )
        return {"status": "triggered", "message": "Sync started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
