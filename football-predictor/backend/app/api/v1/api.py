"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, matches, predictions, teams, leagues, users, admin
from app.api.v1 import logs

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])