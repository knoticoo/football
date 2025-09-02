"""
Prediction endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.prediction import Prediction, PredictionType, PredictionResult
from app.models.user import User
from app.schemas.prediction import PredictionResponse, PredictionCreate, PredictionUpdate
from app.services.prediction_engine import PredictionEngine

router = APIRouter()


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    match_id: Optional[int] = None,
    prediction_type: Optional[PredictionType] = None,
    result: Optional[PredictionResult] = None,
    db: Session = Depends(get_db)
):
    """Get predictions with optional filters"""
    
    query = db.query(Prediction)
    
    # Apply filters
    if user_id:
        query = query.filter(Prediction.user_id == user_id)
    
    if match_id:
        query = query.filter(Prediction.match_id == match_id)
    
    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)
    
    if result:
        query = query.filter(Prediction.result == result)
    
    # Order by creation date
    query = query.order_by(Prediction.created_at.desc())
    
    # Apply pagination
    predictions = query.offset(skip).limit(limit).all()
    
    return predictions


@router.get("/user/{user_id}", response_model=List[PredictionResponse])
async def get_user_predictions(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get predictions for a specific user"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    
    return predictions


@router.get("/match/{match_id}", response_model=List[PredictionResponse])
async def get_match_predictions(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Get all predictions for a specific match"""
    
    predictions = db.query(Prediction).filter(
        Prediction.match_id == match_id
    ).order_by(Prediction.created_at.desc()).all()
    
    return predictions


@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    prediction_data: PredictionCreate,
    db: Session = Depends(get_db)
):
    """Create a new prediction"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == prediction_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if user already has a prediction for this match
    existing_prediction = db.query(Prediction).filter(
        Prediction.user_id == prediction_data.user_id,
        Prediction.match_id == prediction_data.match_id
    ).first()
    
    if existing_prediction:
        raise HTTPException(
            status_code=400,
            detail="User already has a prediction for this match"
        )
    
    # Create prediction
    db_prediction = Prediction(**prediction_data.dict())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: int,
    prediction_data: PredictionUpdate,
    db: Session = Depends(get_db)
):
    """Update a prediction"""
    
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )
    
    # Don't allow updates to resolved predictions
    if prediction.is_resolved:
        raise HTTPException(
            status_code=400,
            detail="Cannot update resolved predictions"
        )
    
    # Update fields
    for field, value in prediction_data.dict(exclude_unset=True).items():
        setattr(prediction, field, value)
    
    db.commit()
    db.refresh(prediction)
    
    return prediction


@router.get("/leaderboard/", response_model=List[dict])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get prediction leaderboard"""
    
    # This would typically use the UserStats model
    # For now, return a simple implementation
    
    leaderboard = db.query(
        User.id,
        User.username,
        User.full_name
    ).limit(limit).all()
    
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "accuracy": 0.0,  # Would be calculated from UserStats
            "total_predictions": 0,  # Would be calculated from UserStats
            "rank": i + 1
        }
        for i, user in enumerate(leaderboard)
    ]


@router.get("/generate/{match_id}")
async def generate_prediction(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Generate AI prediction for a match"""
    
    try:
        prediction_engine = PredictionEngine()
        prediction = prediction_engine.generate_prediction(match_id)
        
        return prediction
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction: {str(e)}"
        )