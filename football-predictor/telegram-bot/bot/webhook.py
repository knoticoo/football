"""
Webhook setup for Telegram bot
"""

import logging
from telegram.ext import Application
from config import config

logger = logging.getLogger(__name__)


async def setup_webhook(application: Application):
    """Setup webhook for the bot"""
    
    try:
        if not config.WEBHOOK_URL:
            logger.warning("WEBHOOK_URL not configured, using polling mode")
            return
        
        # Set webhook
        await application.bot.set_webhook(
            url=config.WEBHOOK_URL,
            allowed_updates=["message", "callback_query"]
        )
        
        logger.info(f"Webhook set to: {config.WEBHOOK_URL}")
        
    except Exception as e:
        logger.error(f"Failed to setup webhook: {e}")
        raise


async def remove_webhook(application: Application):
    """Remove webhook (switch to polling)"""
    
    try:
        await application.bot.delete_webhook()
        logger.info("Webhook removed, switched to polling mode")
        
    except Exception as e:
        logger.error(f"Failed to remove webhook: {e}")


async def get_webhook_info(application: Application):
    """Get webhook information"""
    
    try:
        webhook_info = await application.bot.get_webhook_info()
        
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
        
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        return None