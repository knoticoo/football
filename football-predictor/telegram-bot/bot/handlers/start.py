"""
Start and help command handlers
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

from services.user_service import UserService
from services.api_client import APIClient

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    
    user = update.effective_user
    logger.info(f"Start command from user {user.id} (@{user.username})")
    
    try:
        # Register or get user
        user_service = UserService()
        telegram_user = await user_service.get_or_create_telegram_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Welcome message
        welcome_text = f"""
⚽ Welcome to Football Predictor Bot, {user.first_name}!

🎯 Make accurate football predictions and compete with other users!

📊 Available commands:
• /predict - Make predictions for upcoming matches
• /my_predictions - View your prediction history
• /standings - View league tables
• /fixtures - View upcoming matches
• /stats - Your prediction statistics
• /leaderboard - Top predictors
• /help - Show all commands

🚀 Ready to start predicting? Use /predict to see today's matches!
        """
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("🎯 Make Prediction", callback_data="predict"),
                InlineKeyboardButton("📊 My Stats", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
                InlineKeyboardButton("📅 Fixtures", callback_data="fixtures")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    
    help_text = """
⚽ <b>Football Predictor Bot - Help</b>

<b>🎯 Prediction Commands:</b>
• /predict - Make predictions for upcoming matches
• /my_predictions - View your prediction history
• /stats - Your prediction statistics

<b>📊 Information Commands:</b>
• /standings - View league tables
• /fixtures - View upcoming matches
• /leaderboard - Top predictors

<b>⚙️ User Commands:</b>
• /settings - Manage your preferences
• /subscribe - Subscribe to leagues/teams
• /notifications - Toggle notifications

<b>🔧 Admin Commands:</b>
• /admin_stats - System statistics
• /admin_broadcast - Send message to all users

<b>📱 How to use:</b>
1. Use /predict to see upcoming matches
2. Select a match and make your prediction
3. Track your accuracy with /stats
4. Compete on the /leaderboard

<b>💡 Tips:</b>
• Predictions close 2 hours before match start
• Higher confidence predictions give more points
• Check team form before predicting

Need help? Contact @your_support_username
    """
    
    await update.message.reply_text(help_text, parse_mode='HTML')


# Create handlers
start_handler = CommandHandler("start", start_command)
help_handler = CommandHandler("help", help_command)