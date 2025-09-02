"""
API client for communicating with the backend
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from config import config

logger = logging.getLogger(__name__)


class APIClient:
    """Client for making API requests to the backend"""
    
    def __init__(self):
        self.base_url = f"{config.API_BASE_URL}{config.API_V1_STR}"
        self.timeout = 30.0
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make HTTP request to API"""
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None
    
    # User endpoints
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return await self._make_request("GET", f"/users/{user_id}")
    
    async def create_telegram_user(self, user_data: Dict) -> Optional[Dict]:
        """Create telegram user"""
        return await self._make_request("POST", "/auth/telegram", data=user_data)
    
    async def update_user(self, user_id: int, user_data: Dict) -> Optional[Dict]:
        """Update user"""
        return await self._make_request("PUT", f"/users/{user_id}", data=user_data)
    
    # Match endpoints
    async def get_matches(
        self, 
        skip: int = 0, 
        limit: int = 100,
        league_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """Get matches with filters"""
        params = {"skip": skip, "limit": limit}
        if league_id:
            params["league_id"] = league_id
        if status:
            params["status"] = status
        
        return await self._make_request("GET", "/matches", params=params)
    
    async def get_upcoming_matches(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get upcoming matches"""
        return await self._make_request("GET", f"/matches/upcoming?limit={limit}")
    
    async def get_live_matches(self) -> Optional[List[Dict]]:
        """Get live matches"""
        return await self._make_request("GET", "/matches/live")
    
    async def get_match(self, match_id: int) -> Optional[Dict]:
        """Get specific match"""
        return await self._make_request("GET", f"/matches/{match_id}")
    
    # Prediction endpoints
    async def get_predictions(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        match_id: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """Get predictions with filters"""
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        if match_id:
            params["match_id"] = match_id
        
        return await self._make_request("GET", "/predictions", params=params)
    
    async def get_user_predictions(self, user_id: int, limit: int = 50) -> Optional[List[Dict]]:
        """Get user predictions"""
        return await self._make_request("GET", f"/predictions/user/{user_id}?limit={limit}")
    
    async def create_prediction(self, prediction_data: Dict) -> Optional[Dict]:
        """Create prediction"""
        return await self._make_request("POST", "/predictions", data=prediction_data)
    
    async def get_leaderboard(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get leaderboard"""
        return await self._make_request("GET", f"/predictions/leaderboard/?limit={limit}")
    
    # League endpoints
    async def get_leagues(self, limit: int = 100) -> Optional[List[Dict]]:
        """Get leagues"""
        return await self._make_request("GET", f"/leagues?limit={limit}")
    
    async def get_league(self, league_id: int) -> Optional[Dict]:
        """Get specific league"""
        return await self._make_request("GET", f"/leagues/{league_id}")
    
    async def get_league_table(self, league_id: int) -> Optional[Dict]:
        """Get league table"""
        return await self._make_request("GET", f"/leagues/{league_id}/table")
    
    # Team endpoints
    async def get_teams(self, league_id: Optional[int] = None) -> Optional[List[Dict]]:
        """Get teams"""
        params = {}
        if league_id:
            params["league_id"] = league_id
        
        return await self._make_request("GET", "/teams", params=params)
    
    async def get_team(self, team_id: int) -> Optional[Dict]:
        """Get specific team"""
        return await self._make_request("GET", f"/teams/{team_id}")
    
    async def get_team_stats(self, team_id: int) -> Optional[Dict]:
        """Get team statistics"""
        return await self._make_request("GET", f"/teams/{team_id}/stats")