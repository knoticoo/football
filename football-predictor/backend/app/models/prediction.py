"""
Prediction model for storing user predictions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PredictionType(str, enum.Enum):
    """Prediction type enumeration"""
    WIN_DRAW_WIN = "WIN_DRAW_WIN"  # 1X2
    OVER_UNDER = "OVER_UNDER"      # Over/Under goals
    BOTH_TEAMS_SCORE = "BOTH_TEAMS_SCORE"  # BTTS
    CORRECT_SCORE = "CORRECT_SCORE"        # Exact score
    DOUBLE_CHANCE = "DOUBLE_CHANCE"        # 1X, 12, X2


class PredictionResult(str, enum.Enum):
    """Prediction result enumeration"""
    PENDING = "PENDING"
    WON = "WON"
    LOST = "LOST"
    VOID = "VOID"  # Match postponed/cancelled


class Prediction(Base):
    """Prediction model for storing user predictions"""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and match
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(Enum(PredictionType), nullable=False)
    prediction_value = Column(String(50), nullable=False)  # "1", "X", "2", "Over 2.5", etc.
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Odds and stake (for future betting integration)
    odds = Column(Float, nullable=True)
    stake = Column(Float, nullable=True)
    
    # Result tracking
    result = Column(Enum(PredictionResult), default=PredictionResult.PENDING)
    is_correct = Column(String(10), nullable=True)  # "true", "false", null
    
    # Additional data (JSON string for complex predictions)
    additional_data = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, user_id={self.user_id}, match_id={self.match_id}, type='{self.prediction_type}')>"
    
    @property
    def is_resolved(self):
        """Check if prediction is resolved"""
        return self.result != PredictionResult.PENDING
    
    @property
    def confidence_percentage(self):
        """Get confidence as percentage"""
        return round(self.confidence * 100, 1)