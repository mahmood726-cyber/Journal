"""
User management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.base import get_db
from db.models import User, UserRole
from schemas.user import UserResponse, UserUpdate
from api.auth import get_current_user

router = APIRouter()


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency to check if user has required role.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.EDITOR_IN_CHIEF]))
):
    """
    List all users (admin/editor only).
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can view their own profile, admins/editors can view anyone
    if user.id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.EDITOR_IN_CHIEF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user information.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can only update their own profile
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete by deactivating
    user.is_active = False
    db.commit()

    return {"message": "User deactivated successfully"}


@router.get("/reviewers/available", response_model=List[UserResponse])
async def get_available_reviewers(
    specialization_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]))
):
    """
    Get available reviewers, optionally filtered by specialization.
    """
    query = db.query(User).filter(
        User.role == UserRole.REVIEWER,
        User.is_active == True
    )

    if specialization_id:
        from db.models import user_specializations, Specialization
        query = query.join(user_specializations).filter(
            user_specializations.c.specialization_id == specialization_id
        )

    reviewers = query.all()
    return reviewers
