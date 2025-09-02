"""
Bot scheduler for automated tasks
"""

import logging
import asyncio
from datetime import datetime, time
from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from services.user_service import UserService
from services.match_service import MatchService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def setup_scheduler(application: Application):
    """Setup bot scheduler"""
    
    try:
        # Add scheduled jobs
        scheduler.add_job(
            send_daily_predictions,
            CronTrigger(hour=9, minute=0),  # 9:00 AM UTC
            id="daily_predictions",
            name="Send daily predictions",
            replace_existing=True
        )
        
        scheduler.add_job(
            send_match_reminders,
            CronTrigger(minute=0),  # Every hour
            id="match_reminders",
            name="Send match reminders",
            replace_existing=True
        )
        
        scheduler.add_job(
            update_match_results,
            CronTrigger(minute=30),  # Every 30 minutes
            id="update_results",
            name="Update match results",
            replace_existing=True
        )
        
        scheduler.add_job(
            cleanup_old_data,
            CronTrigger(hour=2, minute=0),  # 2:00 AM UTC daily
            id="cleanup_data",
            name="Cleanup old data",
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}")


async def send_daily_predictions():
    """Send daily predictions to users"""
    
    try:
        logger.info("Starting daily predictions job")
        
        # Get users with notifications enabled
        user_service = UserService()
        # This would typically get users from database
        # For now, we'll skip the actual sending
        
        logger.info("Daily predictions job completed")
        
    except Exception as e:
        logger.error(f"Error in daily predictions job: {e}")


async def send_match_reminders():
    """Send match reminders to users"""
    
    try:
        logger.info("Starting match reminders job")
        
        # Get matches starting in the next hour
        match_service = MatchService()
        # This would typically get upcoming matches and send reminders
        
        logger.info("Match reminders job completed")
        
    except Exception as e:
        logger.error(f"Error in match reminders job: {e}")


async def update_match_results():
    """Update match results and resolve predictions"""
    
    try:
        logger.info("Starting match results update job")
        
        # Get finished matches and update results
        match_service = MatchService()
        # This would typically update match results and resolve predictions
        
        logger.info("Match results update job completed")
        
    except Exception as e:
        logger.error(f"Error in match results update job: {e}")


async def cleanup_old_data():
    """Cleanup old data and logs"""
    
    try:
        logger.info("Starting data cleanup job")
        
        # Cleanup old logs, temporary data, etc.
        # This would typically clean up old data
        
        logger.info("Data cleanup job completed")
        
    except Exception as e:
        logger.error(f"Error in data cleanup job: {e}")


async def send_notification_to_user(bot, user_id: int, message: str):
    """Send notification to specific user"""
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"Notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")


async def send_broadcast_message(bot, user_ids: list, message: str):
    """Send broadcast message to multiple users"""
    
    sent_count = 0
    failed_count = 0
    
    for user_id in user_ids:
        try:
            await send_notification_to_user(bot, user_id, message)
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to user {user_id}: {e}")
            failed_count += 1
    
    logger.info(f"Broadcast completed: {sent_count} sent, {failed_count} failed")
    return sent_count, failed_count


def get_scheduler_status() -> dict:
    """Get scheduler status"""
    
    jobs = scheduler.get_jobs()
    
    return {
        "status": "running" if scheduler.running else "stopped",
        "total_jobs": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]
    }


def stop_scheduler():
    """Stop the scheduler"""
    
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")


def start_scheduler():
    """Start the scheduler"""
    
    try:
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")