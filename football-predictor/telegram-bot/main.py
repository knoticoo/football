"""
Football Prediction Telegram Bot - Main Entry Point
"""

import asyncio
import logging
from telegram.ext import Application
from telegram import Bot

from config import config
from bot.handlers import setup_handlers
from bot.middleware import setup_middleware
from bot.scheduler import setup_scheduler
from bot.webhook import setup_webhook
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Create application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Setup handlers
        setup_handlers(application)
        logger.info("Handlers setup completed")
        
        # Setup middleware
        setup_middleware(application)
        logger.info("Middleware setup completed")
        
        # Setup scheduler
        await setup_scheduler(application)
        logger.info("Scheduler setup completed")
        
        # Setup webhook if configured
        if config.WEBHOOK_URL:
            await setup_webhook(application)
            logger.info(f"Webhook setup completed on port {config.WEBHOOK_PORT}")
        else:
            logger.info("Starting bot in polling mode")
        
        # Start the bot
        if config.WEBHOOK_URL:
            # Webhook mode
            await application.run_webhook(
                listen="0.0.0.0",
                port=config.WEBHOOK_PORT,
                webhook_url=config.WEBHOOK_URL,
                drop_pending_updates=True
            )
        else:
            # Polling mode
            await application.run_polling(drop_pending_updates=True)
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())