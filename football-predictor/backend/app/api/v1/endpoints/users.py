"""
User endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get users with optional filters (admin only)"""
    
    query = db.query(User)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Order by creation date
    query = query.order_by(User.created_at.desc())
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update fields
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            # Hash password if provided
            from app.core.security import get_password_hash
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Soft delete - mark as inactive
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}


@router.get("/{user_id}/stats", response_model=dict)
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Get user stats
    user_stats = user.user_stats
    
    if not user_stats:
        return {
            "user_id": user_id,
            "total_predictions": 0,
            "correct_predictions": 0,
            "accuracy": 0.0,
            "current_streak": 0,
            "global_rank": None
        }
    
    return {
        "user_id": user_id,
        "total_predictions": user_stats.total_predictions,
        "correct_predictions": user_stats.correct_predictions,
        "incorrect_predictions": user_stats.incorrect_predictions,
        "accuracy": user_stats.overall_accuracy,
        "win_rate": user_stats.win_rate,
        "current_streak": user_stats.current_streak,
        "longest_winning_streak": user_stats.longest_winning_streak,
        "longest_losing_streak": user_stats.longest_losing_streak,
        "recent_accuracy": user_stats.recent_accuracy,
        "global_rank": user_stats.global_rank,
        "monthly_rank": user_stats.monthly_rank,
        "total_points": user_stats.total_points,
        "monthly_points": user_stats.monthly_points
    }