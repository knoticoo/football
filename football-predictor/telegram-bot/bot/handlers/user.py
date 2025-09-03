"""
User management command handlers
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from services.user_service import UserService
from services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    
    user = update.effective_user
    logger.info(f"Leaderboard command from user {user.id}")
    
    try:
        # Get leaderboard
        prediction_service = PredictionService()
        leaderboard = await prediction_service.get_leaderboard(limit=10)
        
        if not leaderboard:
            await update.message.reply_text(
                "🏆 No leaderboard data available yet.\n\n"
                "Make some predictions to see the rankings!"
            )
            return
        
        # Format leaderboard
        text = "🏆 <b>Prediction Leaderboard</b>\n\n"
        
        for i, user_data in enumerate(leaderboard, 1):
            username = user_data.get('username', 'Anonymous')
            full_name = user_data.get('full_name', '')
            accuracy = user_data.get('accuracy', 0)
            total_predictions = user_data.get('total_predictions', 0)
            
            # Position emoji
            if i == 1:
                pos_emoji = "🥇"
            elif i == 2:
                pos_emoji = "🥈"
            elif i == 3:
                pos_emoji = "🥉"
            else:
                pos_emoji = f"{i}."
            
            display_name = full_name if full_name else username
            text += f"{pos_emoji} <b>{display_name}</b>\n"
            text += f"   📊 {accuracy:.1f}% accuracy | {total_predictions} predictions\n\n"
        
        # Add filter options
        keyboard = [
            [
                InlineKeyboardButton("📅 This Month", callback_data="leaderboard_monthly"),
                InlineKeyboardButton("📊 All Time", callback_data="leaderboard_all")
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="leaderboard_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in leaderboard command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load leaderboard. Please try again later."
        )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    
    user = update.effective_user
    logger.info(f"Settings command from user {user.id}")
    
    try:
        # Get user settings
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if not telegram_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to register."
            )
            return
        
        # Get current settings
        notification_enabled = telegram_user.get('notification_enabled', True)
        language = telegram_user.get('language', 'en')
        preferred_leagues = telegram_user.get('preferred_leagues', '')
        
        # Format settings
        text = "⚙️ <b>Your Settings</b>\n\n"
        text += f"🔔 Notifications: {'✅ Enabled' if notification_enabled else '❌ Disabled'}\n"
        text += f"🌍 Language: {language.upper()}\n"
        text += f"⚽ Preferred Leagues: {preferred_leagues or 'All'}\n\n"
        text += "Use the buttons below to change your settings:"
        
        # Create settings keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔔 Toggle Notifications", 
                    callback_data=f"toggle_notifications_{not notification_enabled}"
                )
            ],
            [
                InlineKeyboardButton("⚽ Select Leagues", callback_data="select_leagues"),
                InlineKeyboardButton("🌍 Change Language", callback_data="change_language")
            ],
            [
                InlineKeyboardButton("📊 View Stats", callback_data="view_stats"),
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load settings. Please try again later."
        )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
    
    user = update.effective_user
    logger.info(f"Subscribe command from user {user.id}")
    
    try:
        # Get available leagues
        from services.league_service import LeagueService
        league_service = LeagueService()
        leagues = await league_service.get_leagues(limit=10)
        
        if not leagues:
            await update.message.reply_text(
                "⚽ No leagues available for subscription."
            )
            return
        
        # Create subscription keyboard
        keyboard = []
        for league in leagues:
            league_name = league['name']
            country = league.get('country', '')
            
            # Add country flag emoji
            flag_emoji = {
                'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
                'Spain': '🇪🇸',
                'Germany': '🇩🇪',
                'Italy': '🇮🇹',
                'France': '🇫🇷',
                'Netherlands': '🇳🇱'
            }.get(country, '🌍')
            
            button_text = f"{flag_emoji} {league_name}"
            callback_data = f"subscribe_league_{league['id']}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚽ <b>Subscribe to Leagues</b>\n\n"
            "Select leagues to receive notifications for:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in subscribe command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load leagues. Please try again later."
        )


async def toggle_notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle notification toggle callback"""
    
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("toggle_notifications_"):
        return
    
    new_status = query.data.split("_")[2] == "True"
    user = update.effective_user
    
    try:
        # Update user notification setting
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if telegram_user:
            await user_service.update_user_setting(
                user_id=telegram_user['id'],
                setting='notification_enabled',
                value=new_status
            )
            
            status_text = "enabled" if new_status else "disabled"
            await query.edit_message_text(
                f"✅ Notifications {status_text} successfully!\n\n"
                f"Use /settings to change other preferences."
            )
        else:
            await query.edit_message_text("❌ User not found.")
            
    except Exception as e:
        logger.error(f"Error in toggle_notifications_callback: {e}")
        await query.edit_message_text("❌ Sorry, something went wrong.")


async def subscribe_league_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle league subscription callback"""
    
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("subscribe_league_"):
        return
    
    league_id = int(query.data.split("_")[2])
    user = update.effective_user
    
    try:
        # Update user league preferences
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if telegram_user:
            # Get current preferred leagues
            current_leagues = telegram_user.get('preferred_leagues', '')
            leagues_list = current_leagues.split(',') if current_leagues else []
            
            # Toggle league subscription
            league_str = str(league_id)
            if league_str in leagues_list:
                leagues_list.remove(league_str)
                action = "unsubscribed from"
            else:
                leagues_list.append(league_str)
                action = "subscribed to"
            
            new_leagues = ','.join(leagues_list)
            
            await user_service.update_user_setting(
                user_id=telegram_user['id'],
                setting='preferred_leagues',
                value=new_leagues
            )
            
            await query.answer(f"✅ Successfully {action} this league!")
        else:
            await query.edit_message_text("❌ User not found.")
            
    except Exception as e:
        logger.error(f"Error in subscribe_league_callback: {e}")
        await query.answer("❌ Sorry, something went wrong.")


# Create handlers
user_handlers = [
    CommandHandler("leaderboard", leaderboard_command),
    CommandHandler("settings", settings_command),
    CommandHandler("subscribe", subscribe_command),
    CallbackQueryHandler(toggle_notifications_callback, pattern="^toggle_notifications_"),
    CallbackQueryHandler(subscribe_league_callback, pattern="^subscribe_league_"),
]