#!/usr/bin/env python3
"""
Test script to verify Telegram bot configuration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the telegram-bot directory to the path
sys.path.append(str(Path(__file__).parent.parent / "telegram-bot"))

from telegram import Bot
from config import config


async def test_bot():
    """Test bot configuration and connectivity"""
    
    
    try:
        # Create bot instance
        bot = Bot(token=config.BOT_TOKEN)
        
        # Get bot information
        bot_info = await bot.get_me()
        
        
        # Test webhook info if configured
        if config.WEBHOOK_URL:
            webhook_info = await bot.get_webhook_info()
        
        return True
        
    except Exception as e:
        return False


async def main():
    """Main test function"""
    try:
        # Validate configuration
        config.validate()
        
        # Test bot
        success = await test_bot()
        
        if success:
        else:
            sys.exit(1)
            
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())