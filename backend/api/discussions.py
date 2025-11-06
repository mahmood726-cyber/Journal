"""
Discussions API endpoints - Internal messaging for manuscript collaboration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime

from db.base import get_db
from db.models import (
    User,
    Manuscript,
    UserRole,
    Discussion,
    DiscussionMessage,
    DiscussionAttachment,
    ManuscriptFile,
    discussion_participants
)
from schemas.discussions import (
    DiscussionCreate,
    DiscussionResponse,
    DiscussionDetail,
    DiscussionUpdate,
    DiscussionList,
    DiscussionMessageCreate,
    DiscussionMessageResponse,
    AddParticipantsRequest,
    DiscussionParticipant
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service
from core.config import settings

router = APIRouter()


def check_discussion_access(discussion: Discussion, user: User) -> bool:
    """Check if user has access to this discussion."""
    # Editors and admins can access all discussions
    if user.role in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        return True

    # Check if user is a participant
    if user in discussion.participants:
        return True

    # Check if user is the manuscript submitter
    if discussion.manuscript.submitter_id == user.id:
        return True

    return False


@router.get("/", response_model=DiscussionList)
async def list_discussions(
    manuscript_id: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List discussions with filtering.

    - Editors see all discussions
    - Others see only discussions they're part of
    """
    query = db.query(Discussion)

    # Access control
    if current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        # Filter to discussions where user is participant
        query = query.join(discussion_participants).filter(
            discussion_participants.c.user_id == current_user.id
        )

    # Apply filters
    if manuscript_id:
        query = query.filter(Discussion.manuscript_id == manuscript_id)
    if stage:
        query = query.filter(Discussion.stage == stage)
    if status:
        query = query.filter(Discussion.status == status)

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    discussions = query.order_by(Discussion.last_message_at.desc().nullslast(), Discussion.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response
    response_discussions = []
    for disc in discussions:
        # Count messages
        message_count = db.query(DiscussionMessage).filter(
            DiscussionMessage.discussion_id == disc.id
        ).count()

        # Get last message time
        last_message = db.query(DiscussionMessage).filter(
            DiscussionMessage.discussion_id == disc.id
        ).order_by(DiscussionMessage.created_at.desc()).first()

        # Get participants
        participants = [
            DiscussionParticipant(
                user_id=p.id,
                name=f"{p.first_name} {p.last_name}",
                role=p.role.value
            )
            for p in disc.participants
        ]

        response_discussions.append(DiscussionResponse(
            id=disc.id,
            manuscript_id=disc.manuscript_id,
            manuscript_title=disc.manuscript.title,
            stage=disc.stage,
            subject=disc.subject,
            created_by_id=disc.created_by_id,
            created_by_name=f"{disc.created_by.first_name} {disc.created_by.last_name}",
            status=disc.status,
            message_count=message_count,
            last_message_at=last_message.created_at if last_message else None,
            created_at=disc.created_at,
            participants=participants
        ))

    return DiscussionList(
        total=total,
        discussions=response_discussions,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    discussion_data: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new discussion.

    - Automatically adds creator as participant
    - Sends email notifications to all participants
    - Can attach files to initial message
    """
    # Verify manuscript exists
    manuscript = db.query(Manuscript).filter(Manuscript.id == discussion_data.manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Verify participants exist
    participants = db.query(User).filter(User.id.in_(discussion_data.participant_ids)).all()
    if len(participants) != len(discussion_data.participant_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more participant IDs are invalid"
        )

    # Add creator to participants if not already included
    if current_user.id not in discussion_data.participant_ids:
        participants.append(current_user)

    # Create discussion
    new_discussion = Discussion(
        manuscript_id=discussion_data.manuscript_id,
        stage=discussion_data.stage,
        subject=discussion_data.subject,
        created_by_id=current_user.id,
        status='active',
        last_message_at=datetime.now()
    )

    db.add(new_discussion)
    db.flush()

    # Add participants
    for participant in participants:
        new_discussion.participants.append(participant)

    # Create initial message
    initial_message = DiscussionMessage(
        discussion_id=new_discussion.id,
        user_id=current_user.id,
        message=discussion_data.message
    )

    db.add(initial_message)
    db.flush()

    # Attach files if provided
    if discussion_data.file_ids:
        for file_id in discussion_data.file_ids:
            file_obj = db.query(ManuscriptFile).filter(ManuscriptFile.id == file_id).first()
            if file_obj:
                attachment = DiscussionAttachment(
                    discussion_id=new_discussion.id,
                    message_id=initial_message.id,
                    file_id=file_id
                )
                db.add(attachment)

    db.commit()
    db.refresh(new_discussion)

    # Send email notifications to participants (except creator)
    for participant in participants:
        if participant.id != current_user.id:
            try:
                await email_service.send_email(
                    recipients=[participant.email],
                    subject=f"New Discussion: {discussion_data.subject}",
                    template_name="discussion_created",
                    context={
                        'recipient_name': f"{participant.first_name} {participant.last_name}",
                        'creator_name': f"{current_user.first_name} {current_user.last_name}",
                        'subject': discussion_data.subject,
                        'manuscript_title': manuscript.title,
                        'message': discussion_data.message,
                        'discussion_url': f"{settings.FRONTEND_URL}/manuscripts/{manuscript.id}/discussions/{new_discussion.id}"
                    }
                )
            except Exception as e:
                print(f"Failed to send email to {participant.email}: {e}")

    # Build response
    participant_list = [
        DiscussionParticipant(
            user_id=p.id,
            name=f"{p.first_name} {p.last_name}",
            role=p.role.value
        )
        for p in participants
    ]

    return DiscussionResponse(
        id=new_discussion.id,
        manuscript_id=new_discussion.manuscript_id,
        manuscript_title=manuscript.title,
        stage=new_discussion.stage,
        subject=new_discussion.subject,
        created_by_id=new_discussion.created_by_id,
        created_by_name=f"{current_user.first_name} {current_user.last_name}",
        status=new_discussion.status,
        message_count=1,
        last_message_at=datetime.now(),
        created_at=new_discussion.created_at,
        participants=participant_list
    )


@router.get("/{discussion_id}", response_model=DiscussionDetail)
async def get_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get discussion details with all messages."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # Check access
    if not check_discussion_access(discussion, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this discussion"
        )

    # Get all messages
    messages = db.query(DiscussionMessage).filter(
        DiscussionMessage.discussion_id == discussion_id
    ).order_by(DiscussionMessage.created_at).all()

    # Build message responses
    message_responses = []
    for msg in messages:
        # Get attachments
        attachments = db.query(DiscussionAttachment).filter(
            DiscussionAttachment.message_id == msg.id
        ).all()

        attachment_list = [
            {
                'id': att.file_id,
                'name': att.file.file_name,
                'size': att.file.file_size,
                'type': att.file.file_type
            }
            for att in attachments
        ]

        message_responses.append(DiscussionMessageResponse(
            id=msg.id,
            discussion_id=msg.discussion_id,
            user_id=msg.user_id,
            user_name=f"{msg.user.first_name} {msg.user.last_name}",
            user_role=msg.user.role.value,
            message=msg.message,
            attachments=attachment_list,
            created_at=msg.created_at
        ))

    # Get participants
    participants = [
        DiscussionParticipant(
            user_id=p.id,
            name=f"{p.first_name} {p.last_name}",
            role=p.role.value
        )
        for p in discussion.participants
    ]

    return DiscussionDetail(
        id=discussion.id,
        manuscript_id=discussion.manuscript_id,
        manuscript_title=discussion.manuscript.title,
        stage=discussion.stage,
        subject=discussion.subject,
        created_by_id=discussion.created_by_id,
        created_by_name=f"{discussion.created_by.first_name} {discussion.created_by.last_name}",
        status=discussion.status,
        message_count=len(messages),
        last_message_at=messages[-1].created_at if messages else None,
        created_at=discussion.created_at,
        participants=participants,
        messages=message_responses
    )


@router.post("/{discussion_id}/messages", response_model=DiscussionMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    discussion_id: int,
    message_data: DiscussionMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to a discussion.

    - Can attach files
    - Sends email notifications to all participants
    - Updates last_message_at timestamp
    """
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # Check access
    if not check_discussion_access(discussion, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this discussion"
        )

    if discussion.status == 'closed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add messages to closed discussion"
        )

    # Create message
    new_message = DiscussionMessage(
        discussion_id=discussion_id,
        user_id=current_user.id,
        message=message_data.message
    )

    db.add(new_message)
    db.flush()

    # Attach files if provided
    attachments_list = []
    if message_data.file_ids:
        for file_id in message_data.file_ids:
            file_obj = db.query(ManuscriptFile).filter(ManuscriptFile.id == file_id).first()
            if file_obj:
                attachment = DiscussionAttachment(
                    discussion_id=discussion_id,
                    message_id=new_message.id,
                    file_id=file_id
                )
                db.add(attachment)
                attachments_list.append({
                    'id': file_obj.id,
                    'name': file_obj.file_name,
                    'size': file_obj.file_size,
                    'type': file_obj.file_type
                })

    # Update discussion last_message_at
    discussion.last_message_at = datetime.now()

    db.commit()
    db.refresh(new_message)

    # Send email notifications to other participants
    for participant in discussion.participants:
        if participant.id != current_user.id:
            try:
                await email_service.send_email(
                    recipients=[participant.email],
                    subject=f"New Message: {discussion.subject}",
                    template_name="discussion_message",
                    context={
                        'recipient_name': f"{participant.first_name} {participant.last_name}",
                        'sender_name': f"{current_user.first_name} {current_user.last_name}",
                        'subject': discussion.subject,
                        'message': message_data.message,
                        'discussion_url': f"{settings.FRONTEND_URL}/manuscripts/{discussion.manuscript_id}/discussions/{discussion_id}"
                    }
                )
            except Exception as e:
                print(f"Failed to send email to {participant.email}: {e}")

    return DiscussionMessageResponse(
        id=new_message.id,
        discussion_id=new_message.discussion_id,
        user_id=new_message.user_id,
        user_name=f"{current_user.first_name} {current_user.last_name}",
        user_role=current_user.role.value,
        message=new_message.message,
        attachments=attachments_list,
        created_at=new_message.created_at
    )


@router.post("/{discussion_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participants(
    discussion_id: int,
    request: AddParticipantsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add participants to a discussion."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # Only editors and discussion creator can add participants
    if current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        if discussion.created_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only editors or discussion creator can add participants"
            )

    # Get users to add
    users_to_add = db.query(User).filter(User.id.in_(request.user_ids)).all()
    if len(users_to_add) != len(request.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more user IDs are invalid"
        )

    # Add participants (skip if already participant)
    added_count = 0
    for user in users_to_add:
        if user not in discussion.participants:
            discussion.participants.append(user)
            added_count += 1

            # Send notification
            try:
                await email_service.send_email(
                    recipients=[user.email],
                    subject=f"Added to Discussion: {discussion.subject}",
                    template_name="discussion_participant_added",
                    context={
                        'recipient_name': f"{user.first_name} {user.last_name}",
                        'adder_name': f"{current_user.first_name} {current_user.last_name}",
                        'subject': discussion.subject,
                        'discussion_url': f"{settings.FRONTEND_URL}/manuscripts/{discussion.manuscript_id}/discussions/{discussion_id}"
                    }
                )
            except Exception as e:
                print(f"Failed to send email to {user.email}: {e}")

    db.commit()

    return {"message": f"Added {added_count} participant(s) to discussion"}


@router.delete("/{discussion_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    discussion_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a participant from a discussion."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # Only editors and discussion creator can remove participants
    if current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        if discussion.created_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only editors or discussion creator can remove participants"
            )

    # Can't remove the creator
    if user_id == discussion.created_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove discussion creator"
        )

    # Find and remove participant
    user = db.query(User).filter(User.id == user_id).first()
    if user and user in discussion.participants:
        discussion.participants.remove(user)
        db.commit()

    return None


@router.patch("/{discussion_id}", response_model=DiscussionResponse)
async def update_discussion(
    discussion_id: int,
    update_data: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update discussion (change subject or status)."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    # Only editors and discussion creator can update
    if current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        if discussion.created_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only editors or discussion creator can update"
            )

    # Update fields
    if update_data.subject is not None:
        discussion.subject = update_data.subject
    if update_data.status is not None:
        discussion.status = update_data.status

    db.commit()
    db.refresh(discussion)

    # Build response
    message_count = db.query(DiscussionMessage).filter(
        DiscussionMessage.discussion_id == discussion_id
    ).count()

    participants = [
        DiscussionParticipant(
            user_id=p.id,
            name=f"{p.first_name} {p.last_name}",
            role=p.role.value
        )
        for p in discussion.participants
    ]

    return DiscussionResponse(
        id=discussion.id,
        manuscript_id=discussion.manuscript_id,
        manuscript_title=discussion.manuscript.title,
        stage=discussion.stage,
        subject=discussion.subject,
        created_by_id=discussion.created_by_id,
        created_by_name=f"{discussion.created_by.first_name} {discussion.created_by.last_name}",
        status=discussion.status,
        message_count=message_count,
        last_message_at=discussion.last_message_at,
        created_at=discussion.created_at,
        participants=participants
    )


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN])
async def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a discussion (admin/editor only)."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found"
        )

    db.delete(discussion)
    db.commit()

    return None
