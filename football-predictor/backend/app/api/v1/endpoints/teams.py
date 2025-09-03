"""
Team endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.team import Team
from app.models.league import League
from app.schemas.team import TeamResponse, TeamCreate, TeamUpdate

router = APIRouter()


@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    league_id: Optional[int] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get teams with optional filters"""
    
    query = db.query(Team)
    
    # Apply filters
    if league_id:
        query = query.filter(Team.league_id == league_id)
    
    if country:
        query = query.filter(Team.country.ilike(f"%{country}%"))
    
    # Order by name
    query = query.order_by(Team.name)
    
    # Apply pagination
    teams = query.offset(skip).limit(limit).all()
    
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team by ID"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    return team


@router.get("/{team_id}/stats", response_model=dict)
async def get_team_stats(team_id: int, db: Session = Depends(get_db)):
    """Get detailed statistics for a team"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    return {
        "team_id": team.id,
        "team_name": team.name,
        "league": team.league.name if team.league else None,
        "matches_played": team.matches_played,
        "wins": team.wins,
        "draws": team.draws,
        "losses": team.losses,
        "goals_for": team.goals_for,
        "goals_against": team.goals_against,
        "goal_difference": team.goal_difference,
        "points": team.points,
        "position": team.position,
        "win_percentage": team.win_percentage,
        "home_form": team.home_form,
        "away_form": team.away_form,
        "overall_form": team.overall_form,
        "avg_goals_scored": team.avg_goals_scored,
        "avg_goals_conceded": team.avg_goals_conceded,
        "clean_sheets": team.clean_sheets,
        "failed_to_score": team.failed_to_score
    }


@router.post("/", response_model=TeamResponse)
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team (admin only)"""
    
    # Verify league exists
    if team_data.league_id:
        league = db.query(League).filter(League.id == team_data.league_id).first()
        if not league:
            raise HTTPException(
                status_code=400,
                detail="League not found"
            )
    
    # Create team
    db_team = Team(**team_data.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    return db_team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db)
):
    """Update a team (admin only)"""
    
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Update fields
    for field, value in team_data.dict(exclude_unset=True).items():
        setattr(team, field, value)
    
    db.commit()
    db.refresh(team)
    
    return team