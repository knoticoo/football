"""
Match endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.match import Match, MatchStatus
from app.models.team import Team
from app.models.league import League
from app.schemas.match import MatchResponse, MatchCreate, MatchUpdate

router = APIRouter()


@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    league_id: Optional[int] = None,
    team_id: Optional[int] = None,
    status: Optional[MatchStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get matches with optional filters"""
    
    query = db.query(Match)
    
    # Apply filters
    if league_id:
        query = query.filter(Match.league_id == league_id)
    
    if team_id:
        query = query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    
    if status:
        query = query.filter(Match.status == status)
    
    if date_from:
        query = query.filter(Match.match_date >= date_from)
    
    if date_to:
        query = query.filter(Match.match_date <= date_to)
    
    # Order by match date
    query = query.order_by(Match.match_date)
    
    # Apply pagination
    matches = query.offset(skip).limit(limit).all()
    
    return matches


@router.get("/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    limit: int = Query(10, ge=1, le=100),
    league_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get upcoming matches"""
    
    query = db.query(Match).filter(
        Match.status.in_([MatchStatus.SCHEDULED, MatchStatus.TIMED]),
        Match.match_date > datetime.utcnow()
    )
    
    if league_id:
        query = query.filter(Match.league_id == league_id)
    
    matches = query.order_by(Match.match_date).limit(limit).all()
    
    return matches


@router.get("/live", response_model=List[MatchResponse])
async def get_live_matches(db: Session = Depends(get_db)):
    """Get currently live matches"""
    
    matches = db.query(Match).filter(
        Match.status.in_([MatchStatus.IN_PLAY, MatchStatus.PAUSED])
    ).order_by(Match.match_date).all()
    
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get a specific match by ID"""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    return match


@router.post("/", response_model=MatchResponse)
async def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    """Create a new match (admin only)"""
    
    # Verify teams exist
    home_team = db.query(Team).filter(Team.id == match_data.home_team_id).first()
    away_team = db.query(Team).filter(Team.id == match_data.away_team_id).first()
    
    if not home_team or not away_team:
        raise HTTPException(
            status_code=400,
            detail="One or both teams not found"
        )
    
    # Verify league exists
    league = db.query(League).filter(League.id == match_data.league_id).first()
    if not league:
        raise HTTPException(
            status_code=400,
            detail="League not found"
        )
    
    # Create match
    db_match = Match(**match_data.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    return db_match


@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db)
):
    """Update a match (admin only)"""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )
    
    # Update fields
    for field, value in match_data.dict(exclude_unset=True).items():
        setattr(match, field, value)
    
    db.commit()
    db.refresh(match)
    
    return match