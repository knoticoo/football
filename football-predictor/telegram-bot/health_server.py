"""
Simple health check server for Telegram bot
"""

import asyncio
import logging
from aiohttp import web
from config import config

logger = logging.getLogger(__name__)


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "football-predictor-telegram-bot",
        "port": config.WEBHOOK_PORT
    })


async def start_health_server():
    """Start the health check server"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', config.WEBHOOK_PORT)
    await site.start()
    
    logger.info(f"Health server started on port {config.WEBHOOK_PORT}")
    return runner


async def stop_health_server(runner):
    """Stop the health check server"""
    await runner.cleanup()
    logger.info("Health server stopped")