"""
Admin endpoints for system management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.services.data_sync_service import DataSyncService
from app.models.user import User
from app.models.prediction import Prediction
from app.models.match import Match

router = APIRouter()


@router.post("/sync-data")
async def sync_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger data synchronization with external APIs"""
    
    try:
        # Add sync task to background
        data_sync_service = DataSyncService()
        background_tasks.add_task(data_sync_service.sync_all_data)
        
        return {
            "message": "Data synchronization started",
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start data sync: {str(e)}"
        )


@router.get("/system-stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    
    try:
        # Get basic counts
        total_users = db.query(User).count()
        total_predictions = db.query(Prediction).count()
        total_matches = db.query(Match).count()
        
        # Get active users (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(User).filter(
            User.last_login >= thirty_days_ago
        ).count()
        
        # Get predictions by result
        won_predictions = db.query(Prediction).filter(
            Prediction.result == "WON"
        ).count()
        
        lost_predictions = db.query(Prediction).filter(
            Prediction.result == "LOST"
        ).count()
        
        pending_predictions = db.query(Prediction).filter(
            Prediction.result == "PENDING"
        ).count()
        
        # Calculate accuracy
        total_resolved = won_predictions + lost_predictions
        accuracy = (won_predictions / total_resolved * 100) if total_resolved > 0 else 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_predictions": total_predictions,
            "total_matches": total_matches,
            "won_predictions": won_predictions,
            "lost_predictions": lost_predictions,
            "pending_predictions": pending_predictions,
            "accuracy": round(accuracy, 2)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system stats: {str(e)}"
        )


@router.post("/update-match-results")
async def update_match_results(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update match results for finished matches"""
    
    try:
        data_sync_service = DataSyncService()
        background_tasks.add_task(data_sync_service.update_match_results)
        
        return {
            "message": "Match results update started",
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update match results: {str(e)}"
        )


@router.post("/cleanup-data")
async def cleanup_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Clean up old data"""
    
    try:
        data_sync_service = DataSyncService()
        background_tasks.add_task(data_sync_service.cleanup_old_data)
        
        return {
            "message": "Data cleanup started",
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup data: {str(e)}"
        )


@router.get("/health-check")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Test external API connection
        from app.services.football_data_service import FootballDataService
        football_service = FootballDataService()
        
        # Get a simple API response
        competitions = await football_service.get_competitions()
        api_healthy = len(competitions) > 0
        
        return {
            "status": "healthy",
            "database": "connected",
            "external_api": "available" if api_healthy else "unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "external_api": "unavailable",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }