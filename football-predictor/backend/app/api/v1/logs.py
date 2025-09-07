"""
Logs API endpoints for frontend debugging
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.logs_service import logs_service

router = APIRouter()

class LogEntry(BaseModel):
    timestamp: str
    level: str
    component: str
    message: str
    data: Optional[Dict[str, Any]] = None
    sessionId: Optional[str] = None

class LogsRequest(BaseModel):
    logs: List[LogEntry]
    sessionId: Optional[str] = None

class ClearLogsRequest(BaseModel):
    sessionId: Optional[str] = None

@router.post("/logs")
async def save_logs(request: LogsRequest):
    """Save frontend logs"""
    try:
        # Convert Pydantic models to dicts
        logs_data = [log.dict() for log in request.logs]
        
        result = logs_service.save_logs(logs_data, request.sessionId)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs/clear")
async def clear_logs(request: ClearLogsRequest):
    """Clear frontend logs"""
    try:
        result = logs_service.clear_logs(request.sessionId)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(session_id: Optional[str] = None, limit: int = 100):
    """Get frontend logs"""
    try:
        result = logs_service.get_logs(session_id, limit)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))