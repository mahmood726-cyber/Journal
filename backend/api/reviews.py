"""
Peer review management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from db.base import get_db
from db.models import (
    User,
    Manuscript,
    Review,
    ReviewStatus,
    ReviewRecommendation,
    ManuscriptStatus,
    UserRole,
    EditorialDecision,
    DecisionType
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service

router = APIRouter()


# Schemas
class ReviewCreate(BaseModel):
    manuscript_id: int
    reviewer_id: int
    due_days: int = 21


class ReviewUpdate(BaseModel):
    recommendation: Optional[ReviewRecommendation] = None
    score_originality: Optional[int] = None
    score_methodology: Optional[int] = None
    score_significance: Optional[int] = None
    score_clarity: Optional[int] = None
    comments_to_author: Optional[str] = None
    comments_to_editor: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    manuscript_id: int
    reviewer_id: int
    status: ReviewStatus
    invited_at: datetime
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    recommendation: Optional[ReviewRecommendation] = None

    class Config:
        from_attributes = True


class EditorialDecisionCreate(BaseModel):
    manuscript_id: int
    decision: DecisionType
    comments: str


@router.post("/invite", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def invite_reviewer(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]))
):
    """
    Invite a reviewer to review a manuscript.
    """
    # Verify manuscript exists
    manuscript = db.query(Manuscript).filter(Manuscript.id == review_data.manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Verify reviewer exists and has reviewer role
    reviewer = db.query(User).filter(User.id == review_data.reviewer_id).first()
    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer not found"
        )

    if reviewer.role != UserRole.REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a reviewer"
        )

    # Check if already invited
    existing_review = db.query(Review).filter(
        Review.manuscript_id == review_data.manuscript_id,
        Review.reviewer_id == review_data.reviewer_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer already invited for this manuscript"
        )

    # Create review invitation
    due_date = datetime.utcnow() + timedelta(days=review_data.due_days)

    new_review = Review(
        manuscript_id=review_data.manuscript_id,
        reviewer_id=review_data.reviewer_id,
        status=ReviewStatus.PENDING,
        due_date=due_date
    )

    db.add(new_review)

    # Update manuscript status if not already under review
    if manuscript.status == ManuscriptStatus.SUBMITTED:
        manuscript.status = ManuscriptStatus.UNDER_REVIEW

    db.commit()
    db.refresh(new_review)

    # Send invitation email
    await email_service.send_review_invitation(
        reviewer_email=reviewer.email,
        reviewer_name=reviewer.full_name,
        manuscript_id=manuscript.manuscript_id,
        title=manuscript.title,
        abstract=manuscript.abstract,
        due_date=due_date.strftime("%Y-%m-%d")
    )

    return new_review


@router.post("/{review_id}/accept")
async def accept_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept review invitation.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Check if current user is the reviewer
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to accept this review"
        )

    if review.status != ReviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review invitation is not pending"
        )

    # Update status
    review.status = ReviewStatus.IN_PROGRESS
    review.accepted_at = datetime.utcnow()

    db.commit()

    return {"message": "Review accepted successfully"}


@router.post("/{review_id}/decline")
async def decline_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Decline review invitation.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Check if current user is the reviewer
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to decline this review"
        )

    if review.status != ReviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review invitation is not pending"
        )

    # Update status
    review.status = ReviewStatus.DECLINED
    review.declined_at = datetime.utcnow()

    db.commit()

    return {"message": "Review declined"}


@router.put("/{review_id}", response_model=ReviewResponse)
async def submit_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit completed review.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Check if current user is the reviewer
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this review"
        )

    if review.status not in [ReviewStatus.IN_PROGRESS, ReviewStatus.PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is not in progress"
        )

    # Update review
    update_data = review_update.dict(exclude_unset=True)

    # Validate that all required fields are provided
    if not review_update.recommendation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation is required"
        )

    for field, value in update_data.items():
        setattr(review, field, value)

    review.status = ReviewStatus.COMPLETED
    review.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    # Send thank you email
    reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
    manuscript = db.query(Manuscript).filter(Manuscript.id == review.manuscript_id).first()

    await email_service.send_review_complete_notification(
        reviewer_email=reviewer.email,
        reviewer_name=reviewer.full_name,
        manuscript_id=manuscript.manuscript_id
    )

    return review


@router.get("/manuscript/{manuscript_id}", response_model=List[ReviewResponse])
async def get_manuscript_reviews(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]))
):
    """
    Get all reviews for a manuscript (editor only).
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    reviews = db.query(Review).filter(Review.manuscript_id == manuscript_id).all()
    return reviews


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    status: Optional[ReviewStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reviews assigned to current user.
    """
    query = db.query(Review).filter(Review.reviewer_id == current_user.id)

    if status:
        query = query.filter(Review.status == status)

    reviews = query.all()
    return reviews


@router.post("/decision", status_code=status.HTTP_201_CREATED)
async def make_editorial_decision(
    decision_data: EditorialDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]))
):
    """
    Make editorial decision on manuscript.
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == decision_data.manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Create decision record
    new_decision = EditorialDecision(
        manuscript_id=decision_data.manuscript_id,
        editor_id=current_user.id,
        decision=decision_data.decision,
        comments=decision_data.comments
    )

    db.add(new_decision)

    # Update manuscript status based on decision
    status_mapping = {
        DecisionType.DESK_REJECT: ManuscriptStatus.REJECTED,
        DecisionType.SEND_FOR_REVIEW: ManuscriptStatus.UNDER_REVIEW,
        DecisionType.MINOR_REVISIONS: ManuscriptStatus.REVISIONS_REQUIRED,
        DecisionType.MAJOR_REVISIONS: ManuscriptStatus.REVISIONS_REQUIRED,
        DecisionType.ACCEPT: ManuscriptStatus.ACCEPTED,
        DecisionType.REJECT: ManuscriptStatus.REJECTED,
    }

    manuscript.status = status_mapping[decision_data.decision]

    db.commit()

    # Send notification email to corresponding author
    corresponding_author = manuscript.authors[0] if manuscript.authors else None

    if corresponding_author:
        if decision_data.decision == DecisionType.ACCEPT:
            await email_service.send_decision_accept(
                author_email=corresponding_author.email,
                author_name=corresponding_author.full_name,
                manuscript_id=manuscript.manuscript_id,
                title=manuscript.title,
                comments=decision_data.comments
            )
        elif decision_data.decision in [DecisionType.REJECT, DecisionType.DESK_REJECT]:
            await email_service.send_decision_reject(
                author_email=corresponding_author.email,
                author_name=corresponding_author.full_name,
                manuscript_id=manuscript.manuscript_id,
                title=manuscript.title,
                comments=decision_data.comments
            )
        elif decision_data.decision in [DecisionType.MINOR_REVISIONS, DecisionType.MAJOR_REVISIONS]:
            revision_type = "Minor Revisions" if decision_data.decision == DecisionType.MINOR_REVISIONS else "Major Revisions"
            due_days = 21 if decision_data.decision == DecisionType.MINOR_REVISIONS else 45
            due_date = datetime.utcnow() + timedelta(days=due_days)

            await email_service.send_decision_revisions(
                author_email=corresponding_author.email,
                author_name=corresponding_author.full_name,
                manuscript_id=manuscript.manuscript_id,
                title=manuscript.title,
                revision_type=revision_type,
                comments=decision_data.comments,
                due_date=due_date.strftime("%Y-%m-%d")
            )

    return {"message": "Decision recorded successfully", "decision_id": new_decision.id}
