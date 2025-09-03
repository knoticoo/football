"""
League service for managing league operations
"""

import logging
from typing import Dict, Optional, List
from services.api_client import APIClient

logger = logging.getLogger(__name__)


class LeagueService:
    """Service for league-related operations"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def get_leagues(self, limit: int = 100) -> List[Dict]:
        """Get all leagues"""
        
        try:
            leagues = await self.api_client.get_leagues(limit)
            
            if leagues:
                logger.info(f"Retrieved {len(leagues)} leagues")
                return leagues
            else:
                logger.info("No leagues found")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_leagues: {e}")
            return []
    
    async def get_league(self, league_id: int) -> Optional[Dict]:
        """Get specific league"""
        
        try:
            league = await self.api_client.get_league(league_id)
            
            if league:
                logger.info(f"Retrieved league {league_id}")
                return league
            else:
                logger.warning(f"League {league_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_league: {e}")
            return None
    
    async def get_league_table(self, league_id: int) -> Optional[Dict]:
        """Get league table/standings"""
        
        try:
            table = await self.api_client.get_league_table(league_id)
            
            if table:
                logger.info(f"Retrieved table for league {league_id}")
                return table
            else:
                logger.warning(f"Table not found for league {league_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_league_table: {e}")
            return None
    
    async def get_popular_leagues(self) -> List[Dict]:
        """Get popular leagues (most active)"""
        
        try:
            # Get all leagues and sort by activity
            leagues = await self.get_leagues(limit=50)
            
            if leagues:
                # For now, return a predefined list of popular leagues
                popular_league_ids = [39, 140, 78, 135, 61]  # Premier League, La Liga, etc.
                
                popular_leagues = []
                for league in leagues:
                    if league.get('external_id') in popular_league_ids:
                        popular_leagues.append(league)
                
                logger.info(f"Retrieved {len(popular_leagues)} popular leagues")
                return popular_leagues
            else:
                logger.info("No popular leagues found")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_popular_leagues: {e}")
            return []
    
    async def get_league_teams(self, league_id: int) -> List[Dict]:
        """Get teams in a league"""
        
        try:
            # Get league table which includes teams
            table = await self.get_league_table(league_id)
            
            if table and table.get('standings'):
                teams = table['standings']
                logger.info(f"Retrieved {len(teams)} teams for league {league_id}")
                return teams
            else:
                logger.warning(f"No teams found for league {league_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_league_teams: {e}")
            return []
    
    async def get_league_info(self, league_id: int) -> Optional[Dict]:
        """Get comprehensive league information"""
        
        try:
            # Get league details
            league = await self.get_league(league_id)
            
            if not league:
                return None
            
            # Get league table
            table = await self.get_league_table(league_id)
            
            # Get teams
            teams = await self.get_league_teams(league_id)
            
            # Combine information
            league_info = {
                "league": league,
                "table": table,
                "teams": teams,
                "total_teams": len(teams),
                "season": league.get('current_season'),
                "country": league.get('country')
            }
            
            logger.info(f"Retrieved comprehensive info for league {league_id}")
            return league_info
            
        except Exception as e:
            logger.error(f"Error in get_league_info: {e}")
            return None
    
    async def search_leagues(self, query: str) -> List[Dict]:
        """Search leagues by name or country"""
        
        try:
            leagues = await self.get_leagues(limit=100)
            
            if leagues:
                # Filter leagues by query
                query_lower = query.lower()
                matching_leagues = [
                    league for league in leagues
                    if (query_lower in league.get('name', '').lower() or
                        query_lower in league.get('country', '').lower())
                ]
                
                logger.info(f"Found {len(matching_leagues)} leagues matching '{query}'")
                return matching_leagues
            else:
                logger.info(f"No leagues found matching '{query}'")
                return []
                
        except Exception as e:
            logger.error(f"Error in search_leagues: {e}")
            return []
    
    async def get_league_statistics(self, league_id: int) -> Optional[Dict]:
        """Get league statistics"""
        
        try:
            league_info = await self.get_league_info(league_id)
            
            if not league_info:
                return None
            
            teams = league_info.get('teams', [])
            
            if not teams:
                return None
            
            # Calculate statistics
            total_matches = sum(team.get('matches_played', 0) for team in teams)
            total_goals = sum(team.get('goals_for', 0) for team in teams)
            avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0
            
            # Find top scorer and best defense
            top_scorer = max(teams, key=lambda t: t.get('goals_for', 0)) if teams else None
            best_defense = min(teams, key=lambda t: t.get('goals_against', 0)) if teams else None
            
            stats = {
                "league_id": league_id,
                "league_name": league_info['league'].get('name'),
                "total_teams": len(teams),
                "total_matches": total_matches,
                "total_goals": total_goals,
                "avg_goals_per_match": round(avg_goals_per_match, 2),
                "top_scorer": {
                    "team": top_scorer.get('name') if top_scorer else None,
                    "goals": top_scorer.get('goals_for', 0) if top_scorer else 0
                },
                "best_defense": {
                    "team": best_defense.get('name') if best_defense else None,
                    "goals_conceded": best_defense.get('goals_against', 0) if best_defense else 0
                }
            }
            
            logger.info(f"Retrieved statistics for league {league_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error in get_league_statistics: {e}")
            return None