"""
Bot middleware for rate limiting and logging
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Any
from telegram.ext import Application

from config import config

logger = logging.getLogger(__name__)

# Rate limiting storage
user_message_counts = defaultdict(list)
user_last_message = defaultdict(float)


def setup_middleware(application: Application):
    """Setup bot middleware"""
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add rate limiting
    application.add_handler(application.create_handler(
        rate_limit_handler,
        block=False
    ))
    
    logger.info("Middleware setup completed")


async def error_handler(update: Any, context: Any):
    """Global error handler"""
    
    logger.error(f"Update {update} caused error {context.error}")
    
    # Try to send error message to user
    if update and hasattr(update, 'effective_chat'):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, something went wrong. Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


async def rate_limit_handler(update: Any, context: Any):
    """Rate limiting handler"""
    
    if not update or not hasattr(update, 'effective_user'):
        return
    
    user_id = update.effective_user.id
    current_time = time.time()
    
    # Clean old messages (older than rate limit window)
    window_start = current_time - config.RATE_LIMIT_WINDOW
    user_message_counts[user_id] = [
        msg_time for msg_time in user_message_counts[user_id]
        if msg_time > window_start
    ]
    
    # Check rate limit
    if len(user_message_counts[user_id]) >= config.RATE_LIMIT_MESSAGES:
        # Rate limit exceeded
        time_since_last = current_time - user_last_message[user_id]
        if time_since_last < 60:  # Don't spam rate limit messages
            return
        
        user_last_message[user_id] = current_time
        
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⏰ Rate limit exceeded. Please wait {config.RATE_LIMIT_WINDOW} seconds before sending more messages."
            )
        except Exception as e:
            logger.error(f"Failed to send rate limit message: {e}")
        
        return
    
    # Add current message to count
    user_message_counts[user_id].append(current_time)
    user_last_message[user_id] = current_time


def log_user_activity(update: Any, action: str):
    """Log user activity"""
    
    if not update or not hasattr(update, 'effective_user'):
        return
    
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) performed action: {action}")


def is_user_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in config.ADMIN_USER_IDS


def get_user_info(update: Any) -> Dict[str, Any]:
    """Extract user information from update"""
    
    if not update or not hasattr(update, 'effective_user'):
        return {}
    
    user = update.effective_user
    
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_bot": user.is_bot,
        "language_code": user.language_code
    }