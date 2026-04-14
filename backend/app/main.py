"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import plugins, reviews, stats

app = FastAPI(
    title="Internal Plugin Marketplace",
    description="企业内部 Claude Code 插件市场 API",
    version="0.1.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 配置具体前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(plugins.router)
app.include_router(reviews.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Plugin Marketplace API", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}