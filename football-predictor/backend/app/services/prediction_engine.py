"""
Prediction engine for generating match predictions
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.team import Team
from app.models.match import Match, MatchStatus
from app.models.prediction import PredictionType

logger = logging.getLogger(__name__)


class PredictionEngine:
    """Engine for generating match predictions based on various factors"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def generate_prediction(self, match_id: int) -> Dict:
        """Generate prediction for a specific match"""
        try:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                raise ValueError(f"Match {match_id} not found")
            
            if match.status != MatchStatus.SCHEDULED and match.status != MatchStatus.TIMED:
                raise ValueError("Can only predict scheduled matches")
            
            # Get team statistics
            home_team_stats = self._get_team_stats(match.home_team_id)
            away_team_stats = self._get_team_stats(match.away_team_id)
            
            # Generate different types of predictions
            predictions = {
                "match_id": match_id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "match_date": match.match_date,
                "predictions": []
            }
            
            # Win/Draw/Win prediction
            win_draw_win = self._predict_win_draw_win(home_team_stats, away_team_stats)
            predictions["predictions"].append(win_draw_win)
            
            # Over/Under goals prediction
            over_under = self._predict_over_under(home_team_stats, away_team_stats)
            predictions["predictions"].append(over_under)
            
            # Both teams to score prediction
            btts = self._predict_both_teams_score(home_team_stats, away_team_stats)
            predictions["predictions"].append(btts)
            
            # Correct score prediction
            correct_score = self._predict_correct_score(home_team_stats, away_team_stats)
            predictions["predictions"].append(correct_score)
            
            logger.info(f"Generated predictions for match {match_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating prediction for match {match_id}: {e}")
            raise
    
    def _get_team_stats(self, team_id: int) -> Dict:
        """Get team statistics for prediction"""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        
        if not team:
            return {}
        
        # Get recent matches for form calculation
        recent_matches = self.db.query(Match).filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
            Match.status == MatchStatus.FINISHED
        ).order_by(Match.match_date.desc()).limit(10).all()
        
        # Calculate form
        form = self._calculate_form(team, recent_matches)
        
        # Calculate home/away performance
        home_performance = self._calculate_home_performance(team, recent_matches)
        away_performance = self._calculate_away_performance(team, recent_matches)
        
        return {
            "team_id": team_id,
            "name": team.name,
            "position": team.position,
            "points": team.points,
            "matches_played": team.matches_played,
            "wins": team.wins,
            "draws": team.draws,
            "losses": team.losses,
            "goals_for": team.goals_for,
            "goals_against": team.goals_against,
            "avg_goals_scored": team.avg_goals_scored,
            "avg_goals_conceded": team.avg_goals_conceded,
            "form": form,
            "home_performance": home_performance,
            "away_performance": away_performance,
            "clean_sheets": team.clean_sheets,
            "failed_to_score": team.failed_to_score
        }
    
    def _calculate_form(self, team: Team, recent_matches: List[Match]) -> List[str]:
        """Calculate team form from recent matches"""
        form = []
        
        for match in recent_matches[:5]:  # Last 5 matches
            if match.home_team_id == team.id:
                # Home match
                if match.home_score > match.away_score:
                    form.append("W")
                elif match.home_score == match.away_score:
                    form.append("D")
                else:
                    form.append("L")
            else:
                # Away match
                if match.away_score > match.home_score:
                    form.append("W")
                elif match.away_score == match.home_score:
                    form.append("D")
                else:
                    form.append("L")
        
        return form
    
    def _calculate_home_performance(self, team: Team, recent_matches: List[Match]) -> Dict:
        """Calculate home performance statistics"""
        home_matches = [m for m in recent_matches if m.home_team_id == team.id]
        
        if not home_matches:
            return {"wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0}
        
        wins = sum(1 for m in home_matches if m.home_score > m.away_score)
        draws = sum(1 for m in home_matches if m.home_score == m.away_score)
        losses = sum(1 for m in home_matches if m.home_score < m.away_score)
        goals_for = sum(m.home_score for m in home_matches)
        goals_against = sum(m.away_score for m in home_matches)
        
        return {
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "avg_goals_for": goals_for / len(home_matches),
            "avg_goals_against": goals_against / len(home_matches)
        }
    
    def _calculate_away_performance(self, team: Team, recent_matches: List[Match]) -> Dict:
        """Calculate away performance statistics"""
        away_matches = [m for m in recent_matches if m.away_team_id == team.id]
        
        if not away_matches:
            return {"wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0}
        
        wins = sum(1 for m in away_matches if m.away_score > m.home_score)
        draws = sum(1 for m in away_matches if m.away_score == m.home_score)
        losses = sum(1 for m in away_matches if m.away_score < m.home_score)
        goals_for = sum(m.away_score for m in away_matches)
        goals_against = sum(m.home_score for m in away_matches)
        
        return {
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "avg_goals_for": goals_for / len(away_matches),
            "avg_goals_against": goals_against / len(away_matches)
        }
    
    def _predict_win_draw_win(self, home_stats: Dict, away_stats: Dict) -> Dict:
        """Predict Win/Draw/Win outcome"""
        # Calculate win probabilities based on various factors
        home_advantage = 0.1  # 10% home advantage
        
        # Team strength based on position and form
        home_strength = self._calculate_team_strength(home_stats)
        away_strength = self._calculate_team_strength(away_stats)
        
        # Adjust for home advantage
        home_strength += home_advantage
        
        # Calculate probabilities
        total_strength = home_strength + away_strength
        home_prob = home_strength / total_strength
        away_prob = away_strength / total_strength
        draw_prob = 1 - home_prob - away_prob
        
        # Normalize probabilities
        total_prob = home_prob + draw_prob + away_prob
        home_prob /= total_prob
        draw_prob /= total_prob
        away_prob /= total_prob
        
        # Determine prediction
        if home_prob > draw_prob and home_prob > away_prob:
            prediction = "1"
            confidence = home_prob
        elif draw_prob > home_prob and draw_prob > away_prob:
            prediction = "X"
            confidence = draw_prob
        else:
            prediction = "2"
            confidence = away_prob
        
        return {
            "type": "WIN_DRAW_WIN",
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": {
                "home_win": round(home_prob, 3),
                "draw": round(draw_prob, 3),
                "away_win": round(away_prob, 3)
            }
        }
    
    def _predict_over_under(self, home_stats: Dict, away_stats: Dict) -> Dict:
        """Predict Over/Under goals"""
        # Calculate expected goals
        home_expected_goals = home_stats.get("avg_goals_scored", 0)
        away_expected_goals = away_stats.get("avg_goals_scored", 0)
        
        # Adjust for home/away performance
        home_home_goals = home_stats.get("home_performance", {}).get("avg_goals_for", 0)
        away_away_goals = away_stats.get("away_performance", {}).get("avg_goals_for", 0)
        
        # Use more recent performance if available
        if home_home_goals > 0:
            home_expected_goals = (home_expected_goals + home_home_goals) / 2
        if away_away_goals > 0:
            away_expected_goals = (away_expected_goals + away_away_goals) / 2
        
        total_expected_goals = home_expected_goals + away_expected_goals
        
        # Predict Over/Under 2.5 goals
        if total_expected_goals > 2.5:
            prediction = "Over 2.5"
            confidence = min(0.9, (total_expected_goals - 2.5) / 2.5 + 0.5)
        else:
            prediction = "Under 2.5"
            confidence = min(0.9, (2.5 - total_expected_goals) / 2.5 + 0.5)
        
        return {
            "type": "OVER_UNDER",
            "prediction": prediction,
            "confidence": confidence,
            "expected_goals": round(total_expected_goals, 2)
        }
    
    def _predict_both_teams_score(self, home_stats: Dict, away_stats: Dict) -> Dict:
        """Predict Both Teams to Score"""
        # Calculate probability of both teams scoring
        home_scoring_prob = min(0.9, home_stats.get("avg_goals_scored", 0) / 2)
        away_scoring_prob = min(0.9, away_stats.get("avg_goals_scored", 0) / 2)
        
        # Adjust for recent form
        home_form = home_stats.get("form", [])
        away_form = away_stats.get("form", [])
        
        if home_form:
            home_recent_goals = sum(1 for result in home_form if result == "W")
            home_scoring_prob = (home_scoring_prob + home_recent_goals / len(home_form)) / 2
        
        if away_form:
            away_recent_goals = sum(1 for result in away_form if result == "W")
            away_scoring_prob = (away_scoring_prob + away_recent_goals / len(away_form)) / 2
        
        # Calculate BTTS probability
        btts_prob = home_scoring_prob * away_scoring_prob
        
        if btts_prob > 0.5:
            prediction = "Yes"
            confidence = btts_prob
        else:
            prediction = "No"
            confidence = 1 - btts_prob
        
        return {
            "type": "BOTH_TEAMS_SCORE",
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": {
                "home_scoring": round(home_scoring_prob, 3),
                "away_scoring": round(away_scoring_prob, 3),
                "btts": round(btts_prob, 3)
            }
        }
    
    def _predict_correct_score(self, home_stats: Dict, away_stats: Dict) -> Dict:
        """Predict correct score"""
        # Calculate expected goals
        home_expected = home_stats.get("avg_goals_scored", 0)
        away_expected = away_stats.get("avg_goals_scored", 0)
        
        # Round to nearest integer for score prediction
        home_score = round(home_expected)
        away_score = round(away_expected)
        
        # Ensure minimum score of 0
        home_score = max(0, home_score)
        away_score = max(0, away_score)
        
        # Calculate confidence based on how close expected goals are to integers
        home_confidence = 1 - abs(home_expected - home_score)
        away_confidence = 1 - abs(away_expected - away_score)
        confidence = (home_confidence + away_confidence) / 2
        
        # Cap confidence at 0.7 for correct score (very difficult to predict)
        confidence = min(0.7, confidence)
        
        prediction = f"{home_score}-{away_score}"
        
        return {
            "type": "CORRECT_SCORE",
            "prediction": prediction,
            "confidence": confidence,
            "expected_goals": {
                "home": round(home_expected, 2),
                "away": round(away_expected, 2)
            }
        }
    
    def _calculate_team_strength(self, team_stats: Dict) -> float:
        """Calculate overall team strength"""
        # Base strength from league position
        position = team_stats.get("position", 20)
        position_strength = max(0.1, (21 - position) / 20)  # Higher position = stronger
        
        # Form strength
        form = team_stats.get("form", [])
        if form:
            form_strength = sum(1 if result == "W" else 0.5 if result == "D" else 0 for result in form) / len(form)
        else:
            form_strength = 0.5
        
        # Goals ratio strength
        goals_for = team_stats.get("goals_for", 0)
        goals_against = team_stats.get("goals_against", 1)  # Avoid division by zero
        goal_ratio = goals_for / goals_against
        goal_strength = min(1.0, goal_ratio / 2)  # Normalize
        
        # Combine factors
        strength = (position_strength * 0.4 + form_strength * 0.3 + goal_strength * 0.3)
        
        return max(0.1, min(1.0, strength))  # Ensure between 0.1 and 1.0