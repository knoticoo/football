"""
Team model for storing team information
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Team(Base):
    """Team model for storing team information and statistics"""
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True)  # ID from external API
    name = Column(String(100), nullable=False, index=True)
    short_name = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)
    founded = Column(Integer, nullable=True)
    
    # Team details
    venue = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # League relationship
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=True)
    
    # Current season statistics
    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    position = Column(Integer, nullable=True)
    
    # Form and performance metrics
    home_form = Column(String(10), nullable=True)  # Last 5 home matches (W/D/L)
    away_form = Column(String(10), nullable=True)  # Last 5 away matches (W/D/L)
    overall_form = Column(String(10), nullable=True)  # Last 5 matches overall
    
    # Advanced statistics
    avg_goals_scored = Column(Float, default=0.0)
    avg_goals_conceded = Column(Float, default=0.0)
    clean_sheets = Column(Integer, default=0)
    failed_to_score = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', league_id={self.league_id})>"
    
    @property
    def goal_difference(self):
        """Calculate goal difference"""
        return self.goals_for - self.goals_against
    
    @property
    def win_percentage(self):
        """Calculate win percentage"""
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100