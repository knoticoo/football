"""
Team schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TeamBase(BaseModel):
    """Base team schema"""
    external_id: int
    name: str
    short_name: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    venue: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    league_id: Optional[int] = None


class TeamCreate(TeamBase):
    """Schema for team creation"""
    pass


class TeamUpdate(BaseModel):
    """Schema for team updates"""
    external_id: Optional[int] = None
    name: Optional[str] = None
    short_name: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    venue: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    league_id: Optional[int] = None
    matches_played: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    points: Optional[int] = None
    position: Optional[int] = None
    home_form: Optional[str] = None
    away_form: Optional[str] = None
    overall_form: Optional[str] = None
    avg_goals_scored: Optional[float] = None
    avg_goals_conceded: Optional[float] = None
    clean_sheets: Optional[int] = None
    failed_to_score: Optional[int] = None


class TeamResponse(TeamBase):
    """Schema for team responses"""
    id: int
    matches_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    position: Optional[int] = None
    home_form: Optional[str] = None
    away_form: Optional[str] = None
    overall_form: Optional[str] = None
    avg_goals_scored: float = 0.0
    avg_goals_conceded: float = 0.0
    clean_sheets: int = 0
    failed_to_score: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    league: Optional[dict] = None
    
    class Config:
        from_attributes = True