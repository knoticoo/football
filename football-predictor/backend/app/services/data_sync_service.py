"""
Data synchronization service for keeping local data in sync with external APIs
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.league import League
from app.models.team import Team
from app.models.match import Match, MatchStatus
from app.services.football_data_service import FootballDataService

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for synchronizing data with external APIs"""
    
    def __init__(self):
        self.football_data_service = FootballDataService()
        self.db = SessionLocal()
    
    async def sync_all_data(self) -> Dict[str, int]:
        """Sync all data from external APIs"""
        results = {
            "leagues_synced": 0,
            "teams_synced": 0,
            "matches_synced": 0,
            "standings_updated": 0,
            "errors": []
        }
        
        try:
            # Sync competitions/leagues
            leagues_synced = await self.sync_leagues()
            results["leagues_synced"] = leagues_synced
            
            # Sync teams for each league
            teams_synced = await self.sync_teams()
            results["teams_synced"] = teams_synced
            
            # Sync matches
            matches_synced = await self.sync_matches()
            results["matches_synced"] = matches_synced
            
            # Update standings
            standings_updated = await self.update_standings()
            results["standings_updated"] = standings_updated
            
            logger.info(f"Data sync completed: {results}")
            
        except Exception as e:
            logger.error(f"Error in sync_all_data: {e}")
            results["errors"].append(str(e))
        
        finally:
            self.db.close()
        
        return results
    
    async def sync_leagues(self) -> int:
        """Sync leagues from external API"""
        try:
            competitions = await self.football_data_service.get_competitions()
            synced_count = 0
            
            for comp_data in competitions:
                # Check if league already exists
                existing_league = self.db.query(League).filter(
                    League.external_id == comp_data["external_id"]
                ).first()
                
                if existing_league:
                    # Update existing league
                    for key, value in comp_data.items():
                        if hasattr(existing_league, key):
                            setattr(existing_league, key, value)
                    existing_league.updated_at = datetime.utcnow()
                else:
                    # Create new league
                    new_league = League(**comp_data)
                    self.db.add(new_league)
                
                synced_count += 1
            
            self.db.commit()
            logger.info(f"Synced {synced_count} leagues")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing leagues: {e}")
            self.db.rollback()
            return 0
    
    async def sync_teams(self) -> int:
        """Sync teams from external API"""
        try:
            leagues = self.db.query(League).all()
            synced_count = 0
            
            for league in leagues:
                teams_data = await self.football_data_service.get_teams(league.external_id)
                
                for team_data in teams_data:
                    # Check if team already exists
                    existing_team = self.db.query(Team).filter(
                        Team.external_id == team_data["external_id"]
                    ).first()
                    
                    if existing_team:
                        # Update existing team
                        for key, value in team_data.items():
                            if hasattr(existing_team, key):
                                setattr(existing_team, key, value)
                        existing_team.updated_at = datetime.utcnow()
                    else:
                        # Create new team
                        team_data["league_id"] = league.id
                        new_team = Team(**team_data)
                        self.db.add(new_team)
                    
                    synced_count += 1
            
            self.db.commit()
            logger.info(f"Synced {synced_count} teams")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing teams: {e}")
            self.db.rollback()
            return 0
    
    async def sync_matches(self) -> int:
        """Sync matches from external API"""
        try:
            leagues = self.db.query(League).all()
            synced_count = 0
            
            for league in leagues:
                # Get matches for the next 30 days
                matches_data = await self.football_data_service.get_upcoming_matches(
                    league.external_id, days_ahead=30
                )
                
                # Also get recent finished matches
                recent_matches = await self.football_data_service.get_matches(
                    league.external_id,
                    date_from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    date_to=datetime.now().strftime("%Y-%m-%d")
                )
                
                all_matches = matches_data + recent_matches
                
                for match_data in all_matches:
                    # Find teams
                    home_team = self.db.query(Team).filter(
                        Team.name == match_data["home_team_name"],
                        Team.league_id == league.id
                    ).first()
                    
                    away_team = self.db.query(Team).filter(
                        Team.name == match_data["away_team_name"],
                        Team.league_id == league.id
                    ).first()
                    
                    if not home_team or not away_team:
                        logger.warning(f"Teams not found for match: {match_data['home_team_name']} vs {match_data['away_team_name']}")
                        continue
                    
                    # Check if match already exists
                    existing_match = self.db.query(Match).filter(
                        Match.external_id == match_data["external_id"]
                    ).first()
                    
                    if existing_match:
                        # Update existing match
                        existing_match.home_score = match_data.get("home_score")
                        existing_match.away_score = match_data.get("away_score")
                        existing_match.status = match_data.get("status", "SCHEDULED")
                        existing_match.venue = match_data.get("venue")
                        existing_match.referee = match_data.get("referee")
                        existing_match.updated_at = datetime.utcnow()
                    else:
                        # Create new match
                        new_match = Match(
                            external_id=match_data["external_id"],
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            league_id=league.id,
                            match_date=datetime.fromisoformat(match_data["match_date"].replace('Z', '+00:00')),
                            status=match_data.get("status", "SCHEDULED"),
                            matchday=match_data.get("matchday"),
                            stage=match_data.get("stage"),
                            group=match_data.get("group"),
                            home_score=match_data.get("home_score"),
                            away_score=match_data.get("away_score"),
                            venue=match_data.get("venue"),
                            referee=match_data.get("referee")
                        )
                        self.db.add(new_match)
                    
                    synced_count += 1
            
            self.db.commit()
            logger.info(f"Synced {synced_count} matches")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error syncing matches: {e}")
            self.db.rollback()
            return 0
    
    async def update_standings(self) -> int:
        """Update team standings from external API"""
        try:
            leagues = self.db.query(League).all()
            updated_count = 0
            
            for league in leagues:
                standings_data = await self.football_data_service.get_standings(league.external_id)
                
                for standing in standings_data:
                    team = self.db.query(Team).filter(
                        Team.external_id == standing["team_external_id"]
                    ).first()
                    
                    if team:
                        # Update team statistics
                        team.position = standing.get("position")
                        team.points = standing.get("points", 0)
                        team.matches_played = standing.get("matches_played", 0)
                        team.wins = standing.get("wins", 0)
                        team.draws = standing.get("draws", 0)
                        team.losses = standing.get("losses", 0)
                        team.goals_for = standing.get("goals_for", 0)
                        team.goals_against = standing.get("goals_against", 0)
                        team.updated_at = datetime.utcnow()
                        
                        updated_count += 1
            
            self.db.commit()
            logger.info(f"Updated {updated_count} team standings")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating standings: {e}")
            self.db.rollback()
            return 0
    
    async def update_match_results(self) -> int:
        """Update match results for finished matches"""
        try:
            # Get matches that are finished but don't have scores
            finished_matches = self.db.query(Match).filter(
                Match.status == MatchStatus.FINISHED,
                Match.home_score.is_(None)
            ).all()
            
            updated_count = 0
            
            for match in finished_matches:
                # Get updated match data from API
                matches_data = await self.football_data_service.get_matches(
                    match.league.external_id,
                    date_from=match.match_date.strftime("%Y-%m-%d"),
                    date_to=match.match_date.strftime("%Y-%m-%d")
                )
                
                # Find the specific match
                for match_data in matches_data:
                    if (match_data["home_team_name"] == match.home_team.name and
                        match_data["away_team_name"] == match.away_team.name):
                        
                        # Update match with results
                        match.home_score = match_data.get("home_score")
                        match.away_score = match_data.get("away_score")
                        match.status = match_data.get("status", "FINISHED")
                        match.updated_at = datetime.utcnow()
                        
                        updated_count += 1
                        break
            
            self.db.commit()
            logger.info(f"Updated {updated_count} match results")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating match results: {e}")
            self.db.rollback()
            return 0
    
    async def cleanup_old_data(self) -> int:
        """Clean up old data to keep database size manageable"""
        try:
            # Delete matches older than 1 year
            cutoff_date = datetime.now() - timedelta(days=365)
            old_matches = self.db.query(Match).filter(
                Match.match_date < cutoff_date
            ).all()
            
            deleted_count = len(old_matches)
            
            for match in old_matches:
                self.db.delete(match)
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old matches")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            self.db.rollback()
            return 0