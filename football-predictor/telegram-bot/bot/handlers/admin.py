"""
Admin command handlers
"""

import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from services.admin_service import AdminService
from services.user_service import UserService

logger = logging.getLogger(__name__)


async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_stats command"""
    
    user = update.effective_user
    logger.info(f"Admin stats command from user {user.id}")
    
    try:
        # Check if user is admin
        if not await is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        # Get system statistics
        admin_service = AdminService()
        stats = await admin_service.get_system_stats()
        
        # Format stats
        text = "📊 <b>System Statistics</b>\n\n"
        text += f"👥 Total Users: {stats.get('total_users', 0)}\n"
        text += f"🎯 Total Predictions: {stats.get('total_predictions', 0)}\n"
        text += f"⚽ Total Matches: {stats.get('total_matches', 0)}\n"
        text += f"🏆 Total Teams: {stats.get('total_teams', 0)}\n"
        text += f"🌍 Total Leagues: {stats.get('total_leagues', 0)}\n\n"
        
        text += f"📈 <b>Recent Activity</b>\n"
        text += f"• New users today: {stats.get('new_users_today', 0)}\n"
        text += f"• Predictions today: {stats.get('predictions_today', 0)}\n"
        text += f"• Active users (24h): {stats.get('active_users_24h', 0)}\n\n"
        
        text += f"🎯 <b>Prediction Stats</b>\n"
        text += f"• Average accuracy: {stats.get('avg_accuracy', 0):.1f}%\n"
        text += f"• Most popular prediction: {stats.get('popular_prediction', 'N/A')}\n"
        text += f"• Pending predictions: {stats.get('pending_predictions', 0)}\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in admin_stats command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load admin stats. Please try again later."
        )


async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_users command"""
    
    user = update.effective_user
    logger.info(f"Admin users command from user {user.id}")
    
    try:
        # Check if user is admin
        if not await is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        # Get user statistics
        admin_service = AdminService()
        user_stats = await admin_service.get_user_management_stats()
        
        # Format user stats
        text = "👥 <b>User Management</b>\n\n"
        text += f"📊 <b>User Statistics</b>\n"
        text += f"• Total users: {user_stats.get('total_users', 0)}\n"
        text += f"• Active users: {user_stats.get('active_users', 0)}\n"
        text += f"• New users (7 days): {user_stats.get('new_users_7d', 0)}\n"
        text += f"• Telegram users: {user_stats.get('telegram_users', 0)}\n"
        text += f"• Web users: {user_stats.get('web_users', 0)}\n\n"
        
        text += f"🎯 <b>Top Users</b>\n"
        top_users = user_stats.get('top_users', [])
        for i, user_data in enumerate(top_users[:5], 1):
            username = user_data.get('username', 'Anonymous')
            accuracy = user_data.get('accuracy', 0)
            predictions = user_data.get('total_predictions', 0)
            text += f"{i}. {username}: {accuracy:.1f}% ({predictions} preds)\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in admin_users command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load user stats. Please try again later."
        )


async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_broadcast command"""
    
    user = update.effective_user
    logger.info(f"Admin broadcast command from user {user.id}")
    
    try:
        # Check if user is admin
        if not await is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        # Check if message is provided
        if not context.args:
            await update.message.reply_text(
                "📢 <b>Broadcast Message</b>\n\n"
                "Usage: /admin_broadcast <message>\n\n"
                "Example: /admin_broadcast New features are now available!",
                parse_mode='HTML'
            )
            return
        
        # Get message text
        message_text = ' '.join(context.args)
        
        # Get all active users
        admin_service = AdminService()
        users = await admin_service.get_active_users()
        
        if not users:
            await update.message.reply_text("❌ No active users found.")
            return
        
        # Send broadcast message
        sent_count = 0
        failed_count = 0
        
        for user_data in users:
            try:
                telegram_id = user_data.get('telegram_id')
                if telegram_id:
                    await context.bot.send_message(
                        chat_id=telegram_id,
                        text=f"📢 <b>Announcement</b>\n\n{message_text}",
                        parse_mode='HTML'
                    )
                    sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {telegram_id}: {e}")
                failed_count += 1
        
        # Report results
        await update.message.reply_text(
            f"📢 <b>Broadcast Complete</b>\n\n"
            f"✅ Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📊 Total: {len(users)}",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in admin_broadcast command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't send broadcast. Please try again later."
        )


async def admin_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_update command"""
    
    user = update.effective_user
    logger.info(f"Admin update command from user {user.id}")
    
    try:
        # Check if user is admin
        if not await is_admin(user.id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        # Start data update
        await update.message.reply_text("🔄 Starting data update...")
        
        admin_service = AdminService()
        update_results = await admin_service.force_data_update()
        
        # Format results
        text = "✅ <b>Data Update Complete</b>\n\n"
        text += f"⚽ Matches updated: {update_results.get('matches_updated', 0)}\n"
        text += f"🏆 Teams updated: {update_results.get('teams_updated', 0)}\n"
        text += f"🌍 Leagues updated: {update_results.get('leagues_updated', 0)}\n"
        text += f"📊 Predictions resolved: {update_results.get('predictions_resolved', 0)}\n"
        
        if update_results.get('errors'):
            text += f"\n⚠️ Errors: {len(update_results['errors'])}"
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in admin_update command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't update data. Please try again later."
        )


async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    from config import config
    return user_id in config.ADMIN_USER_IDS


# Create handlers
admin_handlers = [
    CommandHandler("admin_stats", admin_stats_command),
    CommandHandler("admin_users", admin_users_command),
    CommandHandler("admin_broadcast", admin_broadcast_command),
    CommandHandler("admin_update", admin_update_command),
]