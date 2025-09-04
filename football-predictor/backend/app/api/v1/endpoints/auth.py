"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import verify_password, create_access_token, get_password_hash

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/telegram", response_model=UserResponse)
async def telegram_auth(telegram_data: dict, db: Session = Depends(get_db)):
    """Authenticate user via Telegram"""
    
    # This would typically validate Telegram auth data
    # For now, we'll create a simple implementation
    
    telegram_id = telegram_data.get("id")
    username = telegram_data.get("username")
    first_name = telegram_data.get("first_name")
    last_name = telegram_data.get("last_name")
    
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram ID is required"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        # Create new user
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            is_verified=True  # Telegram users are considered verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from token"""
    # This would decode and validate the JWT token
    # For now, return a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token validation not implemented yet"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user