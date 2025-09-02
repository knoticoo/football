"""
League schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LeagueBase(BaseModel):
    """Base league schema"""
    external_id: int
    name: str
    country: Optional[str] = None
    type: Optional[str] = None
    logo_url: Optional[str] = None
    flag_url: Optional[str] = None
    current_season: Optional[int] = None
    season_start: Optional[datetime] = None
    season_end: Optional[datetime] = None
    is_active: str = "true"
    is_current: str = "true"
    description: Optional[str] = None


class LeagueCreate(LeagueBase):
    """Schema for league creation"""
    pass


class LeagueUpdate(BaseModel):
    """Schema for league updates"""
    external_id: Optional[int] = None
    name: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    logo_url: Optional[str] = None
    flag_url: Optional[str] = None
    current_season: Optional[int] = None
    season_start: Optional[datetime] = None
    season_end: Optional[datetime] = None
    is_active: Optional[str] = None
    is_current: Optional[str] = None
    description: Optional[str] = None


class LeagueResponse(LeagueBase):
    """Schema for league responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True