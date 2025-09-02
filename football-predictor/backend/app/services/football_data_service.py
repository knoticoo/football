"""
Football Data API service for fetching match data
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


class FootballDataService:
    """Service for fetching data from Football-Data.org API"""
    
    def __init__(self):
        self.base_url = settings.FOOTBALL_DATA_BASE_URL
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.headers = {
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {}
        self.rate_limit_delay = 6  # 10 requests per minute (free tier)
        self.last_request_time = 0
    
    async def _rate_limit(self):
        """Implement rate limiting for free tier"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with rate limiting"""
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded, waiting longer...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return await self._make_request(endpoint, params)
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
    
    async def get_competitions(self) -> List[Dict]:
        """Get available competitions/leagues"""
        try:
            data = await self._make_request("/competitions")
            
            if data and "competitions" in data:
                competitions = []
                for comp in data["competitions"]:
                    # Filter for major leagues only (free tier limitation)
                    if comp.get("id") in [2021, 2014, 2002, 2019, 2015]:  # Premier League, La Liga, etc.
                        competitions.append({
                            "external_id": comp["id"],
                            "name": comp["name"],
                            "country": comp.get("area", {}).get("name", ""),
                            "type": comp.get("type", "LEAGUE"),
                            "logo_url": comp.get("emblem"),
                            "current_season": comp.get("currentSeason", {}).get("startDate"),
                            "is_active": "true",
                            "is_current": "true"
                        })
                
                logger.info(f"Retrieved {len(competitions)} competitions")
                return competitions
            else:
                logger.warning("No competitions data received")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching competitions: {e}")
            return []
    
    async def get_teams(self, competition_id: int) -> List[Dict]:
        """Get teams for a competition"""
        try:
            data = await self._make_request(f"/competitions/{competition_id}/teams")
            
            if data and "teams" in data:
                teams = []
                for team in data["teams"]:
                    teams.append({
                        "external_id": team["id"],
                        "name": team["name"],
                        "short_name": team.get("shortName", team["name"][:3].upper()),
                        "country": team.get("area", {}).get("name", ""),
                        "founded": team.get("founded"),
                        "venue": team.get("venue"),
                        "website": team.get("website"),
                        "logo_url": team.get("crest"),
                        "league_id": competition_id
                    })
                
                logger.info(f"Retrieved {len(teams)} teams for competition {competition_id}")
                return teams
            else:
                logger.warning(f"No teams data received for competition {competition_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching teams for competition {competition_id}: {e}")
            return []
    
    async def get_matches(
        self, 
        competition_id: int, 
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get matches for a competition"""
        try:
            params = {}
            if date_from:
                params["dateFrom"] = date_from
            if date_to:
                params["dateTo"] = date_to
            if status:
                params["status"] = status
            
            data = await self._make_request(f"/competitions/{competition_id}/matches", params)
            
            if data and "matches" in data:
                matches = []
                for match in data["matches"]:
                    # Extract match data
                    home_team = match.get("homeTeam", {})
                    away_team = match.get("awayTeam", {})
                    score = match.get("score", {})
                    
                    matches.append({
                        "external_id": match["id"],
                        "home_team_name": home_team.get("name", ""),
                        "away_team_name": away_team.get("name", ""),
                        "match_date": match.get("utcDate"),
                        "status": match.get("status"),
                        "matchday": match.get("matchday"),
                        "stage": match.get("stage"),
                        "group": match.get("group"),
                        "home_score": score.get("fullTime", {}).get("home"),
                        "away_score": score.get("fullTime", {}).get("away"),
                        "venue": match.get("venue"),
                        "referee": match.get("referees", [{}])[0].get("name") if match.get("referees") else None,
                        "league_id": competition_id
                    })
                
                logger.info(f"Retrieved {len(matches)} matches for competition {competition_id}")
                return matches
            else:
                logger.warning(f"No matches data received for competition {competition_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching matches for competition {competition_id}: {e}")
            return []
    
    async def get_standings(self, competition_id: int) -> List[Dict]:
        """Get standings for a competition"""
        try:
            data = await self._make_request(f"/competitions/{competition_id}/standings")
            
            if data and "standings" in data:
                standings = []
                for standing in data["standings"]:
                    if standing.get("type") == "TOTAL":
                        for team_data in standing.get("table", []):
                            team = team_data.get("team", {})
                            standings.append({
                                "team_external_id": team["id"],
                                "team_name": team["name"],
                                "position": team_data.get("position"),
                                "points": team_data.get("points"),
                                "matches_played": team_data.get("playedGames"),
                                "wins": team_data.get("won"),
                                "draws": team_data.get("draw"),
                                "losses": team_data.get("lost"),
                                "goals_for": team_data.get("goalsFor"),
                                "goals_against": team_data.get("goalsAgainst"),
                                "goal_difference": team_data.get("goalDifference")
                            })
                
                logger.info(f"Retrieved {len(standings)} standings for competition {competition_id}")
                return standings
            else:
                logger.warning(f"No standings data received for competition {competition_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching standings for competition {competition_id}: {e}")
            return []
    
    async def get_upcoming_matches(self, competition_id: int, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming matches for the next N days"""
        try:
            today = datetime.now().date()
            date_from = today.strftime("%Y-%m-%d")
            date_to = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            
            return await self.get_matches(
                competition_id=competition_id,
                date_from=date_from,
                date_to=date_to,
                status="SCHEDULED"
            )
            
        except Exception as e:
            logger.error(f"Error fetching upcoming matches: {e}")
            return []
    
    async def get_live_matches(self, competition_id: int) -> List[Dict]:
        """Get live matches"""
        try:
            return await self.get_matches(
                competition_id=competition_id,
                status="IN_PLAY"
            )
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    async def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """Get recent matches for a team"""
        try:
            data = await self._make_request(f"/teams/{team_id}/matches", {"limit": limit})
            
            if data and "matches" in data:
                matches = []
                for match in data["matches"]:
                    home_team = match.get("homeTeam", {})
                    away_team = match.get("awayTeam", {})
                    score = match.get("score", {})
                    
                    matches.append({
                        "external_id": match["id"],
                        "home_team_name": home_team.get("name", ""),
                        "away_team_name": away_team.get("name", ""),
                        "match_date": match.get("utcDate"),
                        "status": match.get("status"),
                        "home_score": score.get("fullTime", {}).get("home"),
                        "away_score": score.get("fullTime", {}).get("away"),
                        "venue": match.get("venue")
                    })
                
                logger.info(f"Retrieved {len(matches)} matches for team {team_id}")
                return matches
            else:
                logger.warning(f"No matches data received for team {team_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching matches for team {team_id}: {e}")
            return []