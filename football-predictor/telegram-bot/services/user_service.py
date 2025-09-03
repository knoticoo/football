"""
User service for managing user operations
"""

import logging
from typing import Dict, Optional, List
from services.api_client import APIClient

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def get_or_create_telegram_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[Dict]:
        """Get or create telegram user"""
        
        try:
            # Prepare user data
            user_data = {
                "id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            }
            
            # Create user via API
            user = await self.api_client.create_telegram_user(user_data)
            
            if user:
                logger.info(f"Created/retrieved telegram user: {telegram_id}")
                return user
            else:
                logger.error(f"Failed to create/retrieve telegram user: {telegram_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_or_create_telegram_user: {e}")
            return None
    
    async def get_telegram_user(self, telegram_id: int) -> Optional[Dict]:
        """Get telegram user by telegram ID"""
        
        try:
            # This would typically involve a database query
            # For now, we'll use a simple approach
            # In a real implementation, you'd query the database directly
            
            # For demo purposes, return a mock user
            return {
                "id": 1,  # This would be the internal user ID
                "telegram_id": telegram_id,
                "username": "test_user",
                "full_name": "Test User",
                "is_active": True,
                "notification_enabled": True,
                "language": "en",
                "preferred_leagues": ""
            }
            
        except Exception as e:
            logger.error(f"Error in get_telegram_user: {e}")
            return None
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        
        try:
            # Get user predictions
            predictions = await self.api_client.get_user_predictions(user_id, limit=100)
            
            if not predictions:
                return {
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "incorrect_predictions": 0,
                    "accuracy": 0.0,
                    "current_streak": 0,
                    "longest_winning_streak": 0,
                    "longest_losing_streak": 0,
                    "recent_accuracy": 0.0,
                    "global_rank": None,
                    "total_points": 0
                }
            
            # Calculate statistics
            total_predictions = len(predictions)
            correct_predictions = sum(1 for p in predictions if p.get('result') == 'WON')
            incorrect_predictions = sum(1 for p in predictions if p.get('result') == 'LOST')
            
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0.0
            
            # Calculate streaks
            current_streak = 0
            longest_winning_streak = 0
            longest_losing_streak = 0
            
            # Sort predictions by date (newest first)
            sorted_predictions = sorted(predictions, key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Calculate current streak
            for pred in sorted_predictions:
                result = pred.get('result')
                if result == 'WON':
                    current_streak += 1
                elif result == 'LOST':
                    current_streak -= 1
                else:
                    break
            
            # Calculate longest streaks
            temp_winning_streak = 0
            temp_losing_streak = 0
            
            for pred in sorted_predictions:
                result = pred.get('result')
                if result == 'WON':
                    temp_winning_streak += 1
                    temp_losing_streak = 0
                    longest_winning_streak = max(longest_winning_streak, temp_winning_streak)
                elif result == 'LOST':
                    temp_losing_streak += 1
                    temp_winning_streak = 0
                    longest_losing_streak = max(longest_losing_streak, temp_losing_streak)
                else:
                    temp_winning_streak = 0
                    temp_losing_streak = 0
            
            # Calculate recent accuracy (last 10 predictions)
            recent_predictions = sorted_predictions[:10]
            recent_correct = sum(1 for p in recent_predictions if p.get('result') == 'WON')
            recent_accuracy = (recent_correct / len(recent_predictions) * 100) if recent_predictions else 0.0
            
            # Calculate points (simple scoring system)
            total_points = correct_predictions * 10  # 10 points per correct prediction
            
            return {
                "total_predictions": total_predictions,
                "correct_predictions": correct_predictions,
                "incorrect_predictions": incorrect_predictions,
                "accuracy": accuracy,
                "current_streak": current_streak,
                "longest_winning_streak": longest_winning_streak,
                "longest_losing_streak": longest_losing_streak,
                "recent_accuracy": recent_accuracy,
                "global_rank": None,  # Would be calculated from leaderboard
                "total_points": total_points
            }
            
        except Exception as e:
            logger.error(f"Error in get_user_stats: {e}")
            return {
                "total_predictions": 0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "accuracy": 0.0,
                "current_streak": 0,
                "longest_winning_streak": 0,
                "longest_losing_streak": 0,
                "recent_accuracy": 0.0,
                "global_rank": None,
                "total_points": 0
            }
    
    async def update_user_setting(self, user_id: int, setting: str, value: any) -> bool:
        """Update user setting"""
        
        try:
            # Prepare update data
            update_data = {setting: value}
            
            # Update user via API
            result = await self.api_client.update_user(user_id, update_data)
            
            if result:
                logger.info(f"Updated user {user_id} setting {setting}")
                return True
            else:
                logger.error(f"Failed to update user {user_id} setting {setting}")
                return False
                
        except Exception as e:
            logger.error(f"Error in update_user_setting: {e}")
            return False
    
    async def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        
        try:
            user = await self.api_client.get_user(user_id)
            
            if user:
                return {
                    "notification_enabled": user.get('notification_enabled', True),
                    "language": user.get('language', 'en'),
                    "preferred_leagues": user.get('preferred_leagues', '')
                }
            else:
                return {
                    "notification_enabled": True,
                    "language": "en",
                    "preferred_leagues": ""
                }
                
        except Exception as e:
            logger.error(f"Error in get_user_preferences: {e}")
            return {
                "notification_enabled": True,
                "language": "en",
                "preferred_leagues": ""
            }