"""Review API endpoints."""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Body

from app.git_ops import GitRepoReader, GitRepoWriter
from app.models import Submission

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


def is_admin(email: str) -> bool:
    """Check if user is an admin."""
    from app.config import settings
    admins = settings.admin_emails.split(",") if settings.admin_emails else []
    return email.strip() in admins


@router.get("/pending", response_model=List[Submission])
async def get_pending_reviews():
    """Get list of pending submissions for review (admin only)."""
    reader = GitRepoReader()
    submissions = reader.get_pending_submissions()

    # Filter only pending
    pending = [s for s in submissions if s.review_status.status == "pending"]
    return pending


@router.get("/all", response_model=List[Submission])
async def get_all_submissions():
    """Get all submissions (admin only)."""
    reader = GitRepoReader()
    return reader.get_pending_submissions()


@router.post("/{submission_id}/approve")
async def approve_submission(
    submission_id: str,
    reviewer_email: str = Body(embed=True),
    notes: str = Body(default="", embed=True)
):
    """Approve a submission (admin only)."""
    reader = GitRepoReader()
    submission = reader.get_submission(submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.review_status.status != "pending":
        raise HTTPException(status_code=400, detail="Submission already processed")

    writer = GitRepoWriter()
    writer.approve_submission(submission_id, reviewer_email, notes)
    writer.create_tag(f"{submission.plugin.name}-v{submission.plugin.version}")
    writer.commit_changes(f"approve: {submission.plugin.name} approved by {reviewer_email}")

    return {"status": "approved", "plugin_name": submission.plugin.name}


@router.post("/{submission_id}/reject")
async def reject_submission(
    submission_id: str,
    reviewer_email: str = Body(embed=True),
    reason: str = Body(embed=True)
):
    """Reject a submission (admin only)."""
    reader = GitRepoReader()
    submission = reader.get_submission(submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.review_status.status != "pending":
        raise HTTPException(status_code=400, detail="Submission already processed")

    writer = GitRepoWriter()
    writer.reject_submission(submission_id, reviewer_email, reason)
    writer.commit_changes(f"reject: {submission.plugin.name} rejected by {reviewer_email}")

    return {"status": "rejected", "reason": reason}