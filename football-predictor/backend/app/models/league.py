"""
League model for storing league information
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class League(Base):
    """League model for storing league information"""
    
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True)  # ID from external API
    name = Column(String(100), nullable=False, index=True)
    country = Column(String(50), nullable=True)
    type = Column(String(20), nullable=True)  # League, Cup, etc.
    
    # League details
    logo_url = Column(String(500), nullable=True)
    flag_url = Column(String(500), nullable=True)
    
    # Season information
    current_season = Column(Integer, nullable=True)
    season_start = Column(DateTime, nullable=True)
    season_end = Column(DateTime, nullable=True)
    
    # League configuration
    is_active = Column(String(10), default="true")  # String to match API response
    is_current = Column(String(10), default="true")
    
    # Additional info
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teams = relationship("Team", back_populates="league")
    matches = relationship("Match", back_populates="league")
    
    def __repr__(self):
        return f"<League(id={self.id}, name='{self.name}', country='{self.country}')>"