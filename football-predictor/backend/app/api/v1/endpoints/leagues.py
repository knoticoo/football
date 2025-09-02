"""
League endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.league import League
from app.schemas.league import LeagueResponse, LeagueCreate, LeagueUpdate

router = APIRouter()


@router.get("/", response_model=List[LeagueResponse])
async def get_leagues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = None,
    is_active: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get leagues with optional filters"""
    
    query = db.query(League)
    
    # Apply filters
    if country:
        query = query.filter(League.country.ilike(f"%{country}%"))
    
    if is_active:
        query = query.filter(League.is_active == is_active)
    
    # Order by name
    query = query.order_by(League.name)
    
    # Apply pagination
    leagues = query.offset(skip).limit(limit).all()
    
    return leagues


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(league_id: int, db: Session = Depends(get_db)):
    """Get a specific league by ID"""
    
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=404,
            detail="League not found"
        )
    
    return league


@router.get("/{league_id}/teams", response_model=List[dict])
async def get_league_teams(league_id: int, db: Session = Depends(get_db)):
    """Get all teams in a league"""
    
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=404,
            detail="League not found"
        )
    
    teams = db.query(league.teams).order_by(League.teams.property.mapper.class_.position).all()
    
    return [
        {
            "id": team.id,
            "name": team.name,
            "short_name": team.short_name,
            "position": team.position,
            "points": team.points,
            "matches_played": team.matches_played,
            "wins": team.wins,
            "draws": team.draws,
            "losses": team.losses,
            "goals_for": team.goals_for,
            "goals_against": team.goals_against,
            "goal_difference": team.goal_difference,
            "logo_url": team.logo_url
        }
        for team in teams
    ]


@router.get("/{league_id}/table", response_model=dict)
async def get_league_table(league_id: int, db: Session = Depends(get_db)):
    """Get league table/standings"""
    
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=404,
            detail="League not found"
        )
    
    # This would typically be a more complex query
    # For now, return basic league info
    return {
        "league": {
            "id": league.id,
            "name": league.name,
            "country": league.country,
            "season": league.current_season
        },
        "standings": []  # Would be populated with team standings
    }


@router.post("/", response_model=LeagueResponse)
async def create_league(league_data: LeagueCreate, db: Session = Depends(get_db)):
    """Create a new league (admin only)"""
    
    # Create league
    db_league = League(**league_data.dict())
    db.add(db_league)
    db.commit()
    db.refresh(db_league)
    
    return db_league


@router.put("/{league_id}", response_model=LeagueResponse)
async def update_league(
    league_id: int,
    league_data: LeagueUpdate,
    db: Session = Depends(get_db)
):
    """Update a league (admin only)"""
    
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=404,
            detail="League not found"
        )
    
    # Update fields
    for field, value in league_data.dict(exclude_unset=True).items():
        setattr(league, field, value)
    
    db.commit()
    db.refresh(league)
    
    return league