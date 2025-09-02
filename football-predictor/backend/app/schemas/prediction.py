"""
Prediction schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.prediction import PredictionType, PredictionResult


class PredictionBase(BaseModel):
    """Base prediction schema"""
    user_id: int
    match_id: int
    prediction_type: PredictionType
    prediction_value: str
    confidence: float


class PredictionCreate(PredictionBase):
    """Schema for prediction creation"""
    odds: Optional[float] = None
    stake: Optional[float] = None
    additional_data: Optional[str] = None


class PredictionUpdate(BaseModel):
    """Schema for prediction updates"""
    prediction_type: Optional[PredictionType] = None
    prediction_value: Optional[str] = None
    confidence: Optional[float] = None
    odds: Optional[float] = None
    stake: Optional[float] = None
    additional_data: Optional[str] = None


class PredictionResponse(PredictionBase):
    """Schema for prediction responses"""
    id: int
    odds: Optional[float] = None
    stake: Optional[float] = None
    result: PredictionResult = PredictionResult.PENDING
    is_correct: Optional[str] = None
    additional_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    user: Optional[dict] = None
    match: Optional[dict] = None
    
    class Config:
        from_attributes = True