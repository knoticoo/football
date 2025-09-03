"""
Match service for managing match operations
"""

import logging
from typing import Dict, Optional, List
from services.api_client import APIClient

logger = logging.getLogger(__name__)


class MatchService:
    """Service for match-related operations"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def get_upcoming_matches(
        self, 
        limit: int = 10, 
        league_id: Optional[int] = None
    ) -> List[Dict]:
        """Get upcoming matches"""
        
        try:
            matches = await self.api_client.get_upcoming_matches(limit)
            
            if matches:
                logger.info(f"Retrieved {len(matches)} upcoming matches")
                return matches
            else:
                logger.warning("No upcoming matches found")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_upcoming_matches: {e}")
            return []
    
    async def get_live_matches(self) -> List[Dict]:
        """Get live matches"""
        
        try:
            matches = await self.api_client.get_live_matches()
            
            if matches:
                logger.info(f"Retrieved {len(matches)} live matches")
                return matches
            else:
                logger.info("No live matches found")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_live_matches: {e}")
            return []
    
    async def get_match(self, match_id: int) -> Optional[Dict]:
        """Get specific match"""
        
        try:
            match = await self.api_client.get_match(match_id)
            
            if match:
                logger.info(f"Retrieved match {match_id}")
                return match
            else:
                logger.warning(f"Match {match_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_match: {e}")
            return None
    
    async def get_matches_by_league(
        self, 
        league_id: int, 
        limit: int = 20
    ) -> List[Dict]:
        """Get matches by league"""
        
        try:
            matches = await self.api_client.get_matches(
                limit=limit,
                league_id=league_id
            )
            
            if matches:
                logger.info(f"Retrieved {len(matches)} matches for league {league_id}")
                return matches
            else:
                logger.warning(f"No matches found for league {league_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_matches_by_league: {e}")
            return []
    
    async def get_matches_by_team(
        self, 
        team_id: int, 
        limit: int = 10
    ) -> List[Dict]:
        """Get matches by team"""
        
        try:
            # This would typically be a more specific API call
            # For now, we'll get all matches and filter
            matches = await self.api_client.get_matches(limit=100)
            
            if matches:
                # Filter matches for the team
                team_matches = [
                    match for match in matches
                    if (match.get('home_team', {}).get('id') == team_id or 
                        match.get('away_team', {}).get('id') == team_id)
                ]
                
                logger.info(f"Retrieved {len(team_matches)} matches for team {team_id}")
                return team_matches[:limit]
            else:
                logger.warning(f"No matches found for team {team_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_matches_by_team: {e}")
            return []
    
    async def get_todays_matches(self) -> List[Dict]:
        """Get today's matches"""
        
        try:
            # Get upcoming matches and filter for today
            matches = await self.api_client.get_upcoming_matches(limit=50)
            
            if matches:
                from datetime import datetime, date
                today = date.today()
                
                todays_matches = []
                for match in matches:
                    match_date = datetime.fromisoformat(
                        match['match_date'].replace('Z', '+00:00')
                    ).date()
                    
                    if match_date == today:
                        todays_matches.append(match)
                
                logger.info(f"Retrieved {len(todays_matches)} matches for today")
                return todays_matches
            else:
                logger.info("No matches found for today")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_todays_matches: {e}")
            return []
    
    async def get_match_statistics(self, match_id: int) -> Optional[Dict]:
        """Get match statistics"""
        
        try:
            match = await self.get_match(match_id)
            
            if match:
                # Extract statistics from match data
                stats = {
                    "match_id": match_id,
                    "home_team": match.get('home_team', {}),
                    "away_team": match.get('away_team', {}),
                    "venue": match.get('venue'),
                    "referee": match.get('referee'),
                    "status": match.get('status'),
                    "score": {
                        "home": match.get('home_score'),
                        "away": match.get('away_score')
                    },
                    "statistics": match.get('statistics'),
                    "prediction_available": match.get('prediction_available', 'true'),
                    "prediction_confidence": match.get('prediction_confidence')
                }
                
                logger.info(f"Retrieved statistics for match {match_id}")
                return stats
            else:
                logger.warning(f"Could not get statistics for match {match_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_match_statistics: {e}")
            return None
    
    async def is_match_available_for_prediction(self, match_id: int) -> bool:
        """Check if match is available for prediction"""
        
        try:
            match = await self.get_match(match_id)
            
            if not match:
                return False
            
            # Check if prediction is available
            prediction_available = match.get('prediction_available', 'true')
            if prediction_available != 'true':
                return False
            
            # Check match status
            status = match.get('status', 'SCHEDULED')
            if status not in ['SCHEDULED', 'TIMED']:
                return False
            
            # Check if match is not too close (e.g., within 2 hours)
            from datetime import datetime, timedelta
            match_date = datetime.fromisoformat(
                match['match_date'].replace('Z', '+00:00')
            )
            now = datetime.utcnow()
            
            # Allow predictions up to 2 hours before match
            if match_date - now < timedelta(hours=2):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in is_match_available_for_prediction: {e}")
            return False