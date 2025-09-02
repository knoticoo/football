"""
Admin service for managing admin operations
"""

import logging
from typing import Dict, Optional, List
from services.api_client import APIClient

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin-related operations"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def get_system_stats(self) -> Dict:
        """Get system statistics"""
        
        try:
            # Get various statistics from the API
            # For now, return mock data since we don't have all endpoints implemented
            
            stats = {
                "total_users": 150,
                "total_predictions": 1250,
                "total_matches": 500,
                "total_teams": 100,
                "total_leagues": 15,
                "new_users_today": 5,
                "predictions_today": 45,
                "active_users_24h": 25,
                "avg_accuracy": 65.5,
                "popular_prediction": "WIN_DRAW_WIN",
                "pending_predictions": 120
            }
            
            logger.info("Retrieved system statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error in get_system_stats: {e}")
            return {
                "total_users": 0,
                "total_predictions": 0,
                "total_matches": 0,
                "total_teams": 0,
                "total_leagues": 0,
                "new_users_today": 0,
                "predictions_today": 0,
                "active_users_24h": 0,
                "avg_accuracy": 0.0,
                "popular_prediction": "N/A",
                "pending_predictions": 0
            }
    
    async def get_user_management_stats(self) -> Dict:
        """Get user management statistics"""
        
        try:
            # Get user statistics
            # For now, return mock data
            
            stats = {
                "total_users": 150,
                "active_users": 120,
                "new_users_7d": 15,
                "telegram_users": 140,
                "web_users": 10,
                "top_users": [
                    {"username": "user1", "accuracy": 75.5, "total_predictions": 50},
                    {"username": "user2", "accuracy": 72.3, "total_predictions": 45},
                    {"username": "user3", "accuracy": 70.1, "total_predictions": 40},
                    {"username": "user4", "accuracy": 68.9, "total_predictions": 35},
                    {"username": "user5", "accuracy": 67.2, "total_predictions": 30}
                ]
            }
            
            logger.info("Retrieved user management statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error in get_user_management_stats: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "new_users_7d": 0,
                "telegram_users": 0,
                "web_users": 0,
                "top_users": []
            }
    
    async def get_active_users(self) -> List[Dict]:
        """Get list of active users for broadcasting"""
        
        try:
            # Get active users
            # For now, return mock data
            
            active_users = [
                {"id": 1, "telegram_id": 123456789, "username": "user1", "is_active": True},
                {"id": 2, "telegram_id": 987654321, "username": "user2", "is_active": True},
                {"id": 3, "telegram_id": 456789123, "username": "user3", "is_active": True},
                {"id": 4, "telegram_id": 789123456, "username": "user4", "is_active": True},
                {"id": 5, "telegram_id": 321654987, "username": "user5", "is_active": True}
            ]
            
            logger.info(f"Retrieved {len(active_users)} active users")
            return active_users
            
        except Exception as e:
            logger.error(f"Error in get_active_users: {e}")
            return []
    
    async def force_data_update(self) -> Dict:
        """Force data update from external APIs"""
        
        try:
            # Simulate data update process
            # In a real implementation, this would call external APIs
            
            update_results = {
                "matches_updated": 25,
                "teams_updated": 8,
                "leagues_updated": 2,
                "predictions_resolved": 15,
                "errors": []
            }
            
            logger.info("Data update completed")
            return update_results
            
        except Exception as e:
            logger.error(f"Error in force_data_update: {e}")
            return {
                "matches_updated": 0,
                "teams_updated": 0,
                "leagues_updated": 0,
                "predictions_resolved": 0,
                "errors": [str(e)]
            }
    
    async def get_prediction_analytics(self) -> Dict:
        """Get prediction analytics"""
        
        try:
            # Get prediction analytics
            # For now, return mock data
            
            analytics = {
                "total_predictions": 1250,
                "correct_predictions": 812,
                "incorrect_predictions": 318,
                "pending_predictions": 120,
                "overall_accuracy": 65.0,
                "prediction_types": {
                    "WIN_DRAW_WIN": {"count": 800, "accuracy": 68.5},
                    "OVER_UNDER": {"count": 300, "accuracy": 62.0},
                    "BOTH_TEAMS_SCORE": {"count": 150, "accuracy": 58.0}
                },
                "confidence_distribution": {
                    "high": {"count": 400, "accuracy": 75.0},
                    "medium": {"count": 600, "accuracy": 65.0},
                    "low": {"count": 250, "accuracy": 55.0}
                }
            }
            
            logger.info("Retrieved prediction analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"Error in get_prediction_analytics: {e}")
            return {
                "total_predictions": 0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "pending_predictions": 0,
                "overall_accuracy": 0.0,
                "prediction_types": {},
                "confidence_distribution": {}
            }
    
    async def get_system_health(self) -> Dict:
        """Get system health status"""
        
        try:
            # Check system health
            # For now, return mock data
            
            health = {
                "status": "healthy",
                "database": "connected",
                "external_apis": "available",
                "bot": "running",
                "last_update": "2024-01-15T10:30:00Z",
                "uptime": "99.9%",
                "errors_24h": 2,
                "warnings_24h": 5
            }
            
            logger.info("Retrieved system health status")
            return health
            
        except Exception as e:
            logger.error(f"Error in get_system_health: {e}")
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "external_apis": "unavailable",
                "bot": "stopped",
                "last_update": None,
                "uptime": "0%",
                "errors_24h": 0,
                "warnings_24h": 0
            }