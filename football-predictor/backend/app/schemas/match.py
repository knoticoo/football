"""
Match schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.match import MatchStatus


class MatchBase(BaseModel):
    """Base match schema"""
    home_team_id: int
    away_team_id: int
    league_id: int
    match_date: datetime
    status: MatchStatus = MatchStatus.SCHEDULED
    matchday: Optional[int] = None
    stage: Optional[str] = None
    group: Optional[str] = None


class MatchCreate(MatchBase):
    """Schema for match creation"""
    pass


class MatchUpdate(BaseModel):
    """Schema for match updates"""
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    league_id: Optional[int] = None
    match_date: Optional[datetime] = None
    status: Optional[MatchStatus] = None
    matchday: Optional[int] = None
    stage: Optional[str] = None
    group: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_penalties: Optional[int] = None
    away_score_penalties: Optional[int] = None
    home_score_extra_time: Optional[int] = None
    away_score_extra_time: Optional[int] = None
    statistics: Optional[str] = None
    venue: Optional[str] = None
    referee: Optional[str] = None
    prediction_available: Optional[str] = None
    prediction_confidence: Optional[str] = None


class MatchResponse(MatchBase):
    """Schema for match responses"""
    id: int
    external_id: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_penalties: Optional[int] = None
    away_score_penalties: Optional[int] = None
    home_score_extra_time: Optional[int] = None
    away_score_extra_time: Optional[int] = None
    statistics: Optional[str] = None
    venue: Optional[str] = None
    referee: Optional[str] = None
    prediction_available: str = "true"
    prediction_confidence: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    home_team: Optional[dict] = None
    away_team: Optional[dict] = None
    league: Optional[dict] = None
    
    class Config:
        from_attributes = True