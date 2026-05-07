"""Plugin API endpoints."""
import os
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import (
    Plugin, PluginSubmit, PluginSubmitGit,
    Submission, SubmissionTypeInfo, SubmitterInfo, ReviewStatus,
    RatingSubmit, Rating,
)
from app.config import settings
from app.services.file_service import ZipProcessor, GitSyncProcessor

router = APIRouter(prefix="/api/plugins", tags=["plugins"])

# Ensure temp processing directory exists
os.makedirs(settings.temp_processing_dir, exist_ok=True)


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
    _check_pending_name(reader, submission.plugin.name)

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


@router.post("/submit/upload")
async def submit_plugin_upload(
    file: UploadFile = File(...),
    submitter_name: str = Form(...),
    submitter_email: str = Form(...),
    submitter_department: Optional[str] = Form(None),
    submitter_message: Optional[str] = Form(None),
):
    """Submit a plugin by uploading a zip file containing a .claude-plugin/ directory."""
    # Validate file extension
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    # Check file size before processing
    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.max_upload_size_mb}MB limit"
        )

    # Process in temp directory
    try:
        with tempfile.TemporaryDirectory(dir=settings.temp_processing_dir) as tmp:
            zip_path = Path(tmp) / "plugin.zip"
            zip_path.write_bytes(contents)

            extract_dir = Path(tmp) / "extracted"
            extract_dir.mkdir()

            # Extract and validate
            processor = ZipProcessor()
            plugin_metadata = processor.extract_and_validate(zip_path, extract_dir)

            # Check for duplicate name
            reader = GitRepoReader()
            existing = reader.get_plugin(plugin_metadata.name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Plugin '{plugin_metadata.name}' already exists"
                )
            _check_pending_name(reader, plugin_metadata.name)

            # Build submitter info
            now = datetime.now(timezone.utc).isoformat()
            submitter = SubmitterInfo(
                name=submitter_name,
                email=submitter_email,
                department=submitter_department,
                submitted_at=now,
                message=submitter_message
            )

            # Count files and size
            file_count = len(list(extract_dir.rglob("*")))
            total_size = sum(f.stat().st_size for f in extract_dir.rglob("*") if f.is_file())
            type_info = SubmissionTypeInfo(
                method="upload",
                source_url=file.filename,
                file_count=file_count,
                total_size_bytes=total_size
            )

            # Create submission
            submission_id = (
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
                f"-{uuid.uuid4().hex[:8]}"
            )
            writer = GitRepoWriter()
            writer.create_file_based_submission(
                submission_id, plugin_metadata, submitter, extract_dir, type_info
            )
            writer.commit_changes(
                f"upload submission: {plugin_metadata.name} by {submitter_email}"
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"submission_id": submission_id, "status": "pending"}


@router.post("/submit/git-sync")
async def submit_plugin_git(body: PluginSubmitGit):
    """Submit a plugin by syncing from a Git repository."""
    # Process in temp directory
    try:
        with tempfile.TemporaryDirectory(dir=settings.temp_processing_dir) as tmp:
            clone_dir = Path(tmp) / "cloned"
            clone_dir.mkdir()

            # Clone and validate
            processor = GitSyncProcessor()
            plugin_metadata = processor.clone_and_validate(
                body.git_url, clone_dir, body.git_ref, body.git_token
            )

            # Check for duplicate name
            reader = GitRepoReader()
            existing = reader.get_plugin(plugin_metadata.name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Plugin '{plugin_metadata.name}' already exists"
                )
            _check_pending_name(reader, plugin_metadata.name)

            # Build submitter
            now = datetime.now(timezone.utc).isoformat()
            submitter = body.submitter
            submitter.submitted_at = now

            # Count files and size
            file_count = len(list(clone_dir.rglob("*")))
            total_size = sum(f.stat().st_size for f in clone_dir.rglob("*") if f.is_file())
            type_info = SubmissionTypeInfo(
                method="git-sync",
                source_url=body.git_url,
                source_ref=body.git_ref,
                file_count=file_count,
                total_size_bytes=total_size
            )

            # Create submission
            submission_id = (
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
                f"-{uuid.uuid4().hex[:8]}"
            )
            writer = GitRepoWriter()
            writer.create_file_based_submission(
                submission_id, plugin_metadata, submitter, clone_dir, type_info
            )
            writer.commit_changes(
                f"git-sync submission: {plugin_metadata.name} by {submitter.email}"
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"submission_id": submission_id, "status": "pending"}


@router.get("/submissions/{submission_id}/files")
async def list_submission_files(submission_id: str):
    """List files in a submission's file bundle (for admin review)."""
    reader = GitRepoReader()
    submission = reader.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    files_dir = reader.repo_path / "pending" / "submissions" / submission_id / "files"
    if not files_dir.exists():
        return {"files": [], "submission_type": None}

    tree = []
    for f in sorted(files_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(files_dir)
            tree.append({"path": str(rel), "size": f.stat().st_size})

    # Read submission type info
    type_file = reader.repo_path / "pending" / "submissions" / submission_id / "submission_type.json"
    type_data = reader._read_json(type_file) if type_file.exists() else None

    return {"files": tree, "submission_type": type_data}


def _check_pending_name(reader: GitRepoReader, name: str) -> None:
    """Check if a plugin name already has a pending submission."""
    for s in reader.get_pending_submissions():
        if s.plugin.name == name and s.review_status.status == "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Plugin '{name}' already has a pending submission"
            )


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