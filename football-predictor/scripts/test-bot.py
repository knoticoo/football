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
    
    print("🤖 Testing Telegram Bot Configuration...")
    print(f"Bot Token: {config.BOT_TOKEN[:10]}...{config.BOT_TOKEN[-10:]}")
    print(f"Bot Username: {config.BOT_USERNAME}")
    print(f"API Base URL: {config.API_BASE_URL}")
    print(f"Webhook Port: {config.WEBHOOK_PORT}")
    print(f"Webhook URL: {config.WEBHOOK_URL or 'Not configured (using polling)'}")
    
    try:
        # Create bot instance
        bot = Bot(token=config.BOT_TOKEN)
        
        # Get bot information
        bot_info = await bot.get_me()
        
        print("\n✅ Bot Configuration Valid!")
        print(f"Bot ID: {bot_info.id}")
        print(f"Bot Name: {bot_info.first_name}")
        print(f"Bot Username: @{bot_info.username}")
        print(f"Can Join Groups: {bot_info.can_join_groups}")
        print(f"Can Read All Group Messages: {bot_info.can_read_all_group_messages}")
        print(f"Supports Inline Queries: {bot_info.supports_inline_queries}")
        
        # Test webhook info if configured
        if config.WEBHOOK_URL:
            webhook_info = await bot.get_webhook_info()
            print(f"\n📡 Webhook Info:")
            print(f"Webhook URL: {webhook_info.url}")
            print(f"Pending Updates: {webhook_info.pending_update_count}")
            if webhook_info.last_error_date:
                print(f"Last Error: {webhook_info.last_error_message}")
        else:
            print("\n🔄 Bot will run in polling mode")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Bot Configuration Error: {e}")
        return False


async def main():
    """Main test function"""
    try:
        # Validate configuration
        config.validate()
        print("✅ Configuration validation passed")
        
        # Test bot
        success = await test_bot()
        
        if success:
            print("\n🎉 Bot is ready to use!")
            print("\nNext steps:")
            print("1. Start the bot: docker compose up telegram-bot")
            print("2. Send /start to @CodyTips_Bot in Telegram")
            print("3. Check logs: docker compose logs -f telegram-bot")
        else:
            print("\n💥 Bot configuration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())