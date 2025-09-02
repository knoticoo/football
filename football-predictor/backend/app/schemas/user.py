"""
User schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    telegram_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(UserBase):
    """Schema for user updates"""
    password: Optional[str] = None
    preferred_leagues: Optional[str] = None
    notification_enabled: Optional[bool] = None
    language: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool
    is_verified: bool
    preferred_leagues: Optional[str] = None
    notification_enabled: bool
    language: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    user: UserResponse


class TelegramAuth(BaseModel):
    """Telegram authentication schema"""
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None