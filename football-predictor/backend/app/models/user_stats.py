"""
User statistics model for tracking user performance
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserStats(Base):
    """User statistics model for tracking prediction performance"""
    
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Overall statistics
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    incorrect_predictions = Column(Integer, default=0)
    void_predictions = Column(Integer, default=0)
    
    # Accuracy metrics
    overall_accuracy = Column(Float, default=0.0)  # Percentage
    win_rate = Column(Float, default=0.0)  # Percentage
    
    # Streaks
    current_streak = Column(Integer, default=0)  # Current winning/losing streak
    longest_winning_streak = Column(Integer, default=0)
    longest_losing_streak = Column(Integer, default=0)
    
    # Recent performance (last 10 predictions)
    recent_accuracy = Column(Float, default=0.0)
    
    # Monthly statistics
    monthly_predictions = Column(Integer, default=0)
    monthly_correct = Column(Integer, default=0)
    monthly_accuracy = Column(Float, default=0.0)
    
    # Ranking
    global_rank = Column(Integer, nullable=True)
    monthly_rank = Column(Integer, nullable=True)
    
    # Points system (for gamification)
    total_points = Column(Integer, default=0)
    monthly_points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_prediction_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_stats")
    
    def __repr__(self):
        return f"<UserStats(user_id={self.user_id}, accuracy={self.overall_accuracy}%, rank={self.global_rank})>"
    
    def update_accuracy(self):
        """Update accuracy based on current predictions"""
        if self.total_predictions > 0:
            self.overall_accuracy = (self.correct_predictions / self.total_predictions) * 100
        else:
            self.overall_accuracy = 0.0
    
    def update_win_rate(self):
        """Update win rate based on resolved predictions"""
        resolved = self.correct_predictions + self.incorrect_predictions
        if resolved > 0:
            self.win_rate = (self.correct_predictions / resolved) * 100
        else:
            self.win_rate = 0.0