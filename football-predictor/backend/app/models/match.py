"""
Match model for storing match information
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MatchStatus(str, enum.Enum):
    """Match status enumeration"""
    SCHEDULED = "SCHEDULED"
    TIMED = "TIMED"
    IN_PLAY = "IN_PLAY"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    SUSPENDED = "SUSPONED"
    CANCELED = "CANCELED"


class Match(Base):
    """Match model for storing match information"""
    
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True)  # ID from external API
    
    # Teams
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # League
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    
    # Match details
    match_date = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED, index=True)
    matchday = Column(Integer, nullable=True)
    stage = Column(String(50), nullable=True)
    group = Column(String(50), nullable=True)
    
    # Score information
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_score_penalties = Column(Integer, nullable=True)
    away_score_penalties = Column(Integer, nullable=True)
    home_score_extra_time = Column(Integer, nullable=True)
    away_score_extra_time = Column(Integer, nullable=True)
    
    # Match statistics (JSON string)
    statistics = Column(Text, nullable=True)
    
    # Venue information
    venue = Column(String(100), nullable=True)
    referee = Column(String(100), nullable=True)
    
    # Prediction related
    prediction_available = Column(String(10), default="true")
    prediction_confidence = Column(String(10), nullable=True)  # HIGH, MEDIUM, LOW
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    league = relationship("League", back_populates="matches")
    predictions = relationship("Prediction", back_populates="match")
    
    def __repr__(self):
        return f"<Match(id={self.id}, {self.home_team.name} vs {self.away_team.name}, {self.match_date})>"
    
    @property
    def is_finished(self):
        """Check if match is finished"""
        return self.status == MatchStatus.FINISHED
    
    @property
    def is_upcoming(self):
        """Check if match is upcoming"""
        return self.status in [MatchStatus.SCHEDULED, MatchStatus.TIMED]
    
    @property
    def is_live(self):
        """Check if match is currently live"""
        return self.status in [MatchStatus.IN_PLAY, MatchStatus.PAUSED]