"""
Prediction service for managing prediction operations
"""

import logging
from typing import Dict, Optional, List
from services.api_client import APIClient

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for prediction-related operations"""
    
    def __init__(self):
        self.api_client = APIClient()
    
    async def create_prediction(
        self, 
        user_id: int, 
        match_id: int, 
        prediction_type: str,
        prediction_value: str,
        confidence: float,
        additional_data: Optional[str] = None
    ) -> Optional[Dict]:
        """Create a new prediction"""
        
        try:
            # Prepare prediction data
            prediction_data = {
                "user_id": user_id,
                "match_id": match_id,
                "prediction_type": prediction_type,
                "prediction_value": prediction_value,
                "confidence": confidence,
                "additional_data": additional_data
            }
            
            # Create prediction via API
            prediction = await self.api_client.create_prediction(prediction_data)
            
            if prediction:
                logger.info(f"Created prediction for user {user_id}, match {match_id}")
                return prediction
            else:
                logger.error(f"Failed to create prediction for user {user_id}, match {match_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error in create_prediction: {e}")
            return None
    
    async def get_user_predictions(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Dict]:
        """Get user predictions"""
        
        try:
            predictions = await self.api_client.get_user_predictions(user_id, limit)
            
            if predictions:
                logger.info(f"Retrieved {len(predictions)} predictions for user {user_id}")
                return predictions
            else:
                logger.info(f"No predictions found for user {user_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_user_predictions: {e}")
            return []
    
    async def get_user_match_prediction(
        self, 
        user_id: int, 
        match_id: int
    ) -> Optional[Dict]:
        """Get user's prediction for a specific match"""
        
        try:
            # Get all user predictions and filter for the match
            predictions = await self.get_user_predictions(user_id, limit=100)
            
            for prediction in predictions:
                if prediction.get('match_id') == match_id:
                    logger.info(f"Found prediction for user {user_id}, match {match_id}")
                    return prediction
            
            logger.info(f"No prediction found for user {user_id}, match {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error in get_user_match_prediction: {e}")
            return None
    
    async def get_match_predictions(self, match_id: int) -> List[Dict]:
        """Get all predictions for a match"""
        
        try:
            predictions = await self.api_client.get_predictions(match_id=match_id)
            
            if predictions:
                logger.info(f"Retrieved {len(predictions)} predictions for match {match_id}")
                return predictions
            else:
                logger.info(f"No predictions found for match {match_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_match_predictions: {e}")
            return []
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get prediction leaderboard"""
        
        try:
            leaderboard = await self.api_client.get_leaderboard(limit)
            
            if leaderboard:
                logger.info(f"Retrieved leaderboard with {len(leaderboard)} users")
                return leaderboard
            else:
                logger.info("No leaderboard data available")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_leaderboard: {e}")
            return []
    
    async def get_user_prediction_stats(self, user_id: int) -> Dict:
        """Get user prediction statistics"""
        
        try:
            predictions = await self.get_user_predictions(user_id, limit=1000)
            
            if not predictions:
                return {
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "incorrect_predictions": 0,
                    "pending_predictions": 0,
                    "accuracy": 0.0,
                    "win_rate": 0.0
                }
            
            # Calculate statistics
            total_predictions = len(predictions)
            correct_predictions = sum(1 for p in predictions if p.get('result') == 'WON')
            incorrect_predictions = sum(1 for p in predictions if p.get('result') == 'LOST')
            pending_predictions = sum(1 for p in predictions if p.get('result') == 'PENDING')
            
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0.0
            
            # Win rate (excluding pending predictions)
            resolved_predictions = correct_predictions + incorrect_predictions
            win_rate = (correct_predictions / resolved_predictions * 100) if resolved_predictions > 0 else 0.0
            
            return {
                "total_predictions": total_predictions,
                "correct_predictions": correct_predictions,
                "incorrect_predictions": incorrect_predictions,
                "pending_predictions": pending_predictions,
                "accuracy": accuracy,
                "win_rate": win_rate
            }
            
        except Exception as e:
            logger.error(f"Error in get_user_prediction_stats: {e}")
            return {
                "total_predictions": 0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "pending_predictions": 0,
                "accuracy": 0.0,
                "win_rate": 0.0
            }
    
    async def get_prediction_types(self) -> List[str]:
        """Get available prediction types"""
        
        return [
            "WIN_DRAW_WIN",      # 1X2
            "OVER_UNDER",        # Over/Under goals
            "BOTH_TEAMS_SCORE",  # BTTS
            "CORRECT_SCORE",     # Exact score
            "DOUBLE_CHANCE"      # 1X, 12, X2
        ]
    
    async def validate_prediction(
        self, 
        prediction_type: str, 
        prediction_value: str
    ) -> bool:
        """Validate prediction value for given type"""
        
        try:
            if prediction_type == "WIN_DRAW_WIN":
                return prediction_value in ["1", "X", "2"]
            elif prediction_type == "OVER_UNDER":
                return prediction_value in ["Over 0.5", "Over 1.5", "Over 2.5", "Over 3.5", 
                                          "Under 0.5", "Under 1.5", "Under 2.5", "Under 3.5"]
            elif prediction_type == "BOTH_TEAMS_SCORE":
                return prediction_value in ["Yes", "No"]
            elif prediction_type == "CORRECT_SCORE":
                # Validate score format (e.g., "2-1", "0-0")
                parts = prediction_value.split("-")
                return len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit()
            elif prediction_type == "DOUBLE_CHANCE":
                return prediction_value in ["1X", "12", "X2"]
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error in validate_prediction: {e}")
            return False
    
    async def get_prediction_confidence_suggestions(self, match_id: int) -> Dict:
        """Get confidence level suggestions based on match analysis"""
        
        try:
            # This would typically involve complex analysis
            # For now, return basic suggestions
            
            return {
                "high_confidence": {
                    "description": "Strong favorite with clear form advantage",
                    "confidence_range": [0.7, 1.0]
                },
                "medium_confidence": {
                    "description": "Balanced match with some indicators",
                    "confidence_range": [0.5, 0.7]
                },
                "low_confidence": {
                    "description": "Uncertain outcome, many variables",
                    "confidence_range": [0.3, 0.5]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_prediction_confidence_suggestions: {e}")
            return {}