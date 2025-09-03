"""
Prediction command handlers
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from services.match_service import MatchService
from services.prediction_service import PredictionService
from services.user_service import UserService

logger = logging.getLogger(__name__)


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /predict command"""
    
    user = update.effective_user
    logger.info(f"Predict command from user {user.id}")
    
    try:
        # Get upcoming matches
        match_service = MatchService()
        matches = await match_service.get_upcoming_matches(limit=5)
        
        if not matches:
            await update.message.reply_text(
                "📅 No upcoming matches available for prediction right now.\n\n"
                "Check back later or use /fixtures to see all upcoming matches!"
            )
            return
        
        # Create match selection keyboard
        keyboard = []
        for match in matches:
            match_text = f"{match['home_team']['name']} vs {match['away_team']['name']}"
            match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
            date_str = match_date.strftime("%d/%m %H:%M")
            
            button_text = f"{match_text}\n{date_str}"
            callback_data = f"predict_match_{match['id']}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        keyboard.append([InlineKeyboardButton("📅 View All Matches", callback_data="all_matches")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 <b>Select a match to predict:</b>\n\n"
            "Choose from the upcoming matches below:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in predict command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load matches. Please try again later."
        )


async def my_predictions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /my_predictions command"""
    
    user = update.effective_user
    logger.info(f"My predictions command from user {user.id}")
    
    try:
        # Get user predictions
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if not telegram_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to register."
            )
            return
        
        prediction_service = PredictionService()
        predictions = await prediction_service.get_user_predictions(
            user_id=telegram_user['id'], 
            limit=10
        )
        
        if not predictions:
            await update.message.reply_text(
                "📝 You haven't made any predictions yet!\n\n"
                "Use /predict to make your first prediction."
            )
            return
        
        # Format predictions
        text = "📝 <b>Your Recent Predictions:</b>\n\n"
        
        for pred in predictions:
            match = pred['match']
            match_text = f"{match['home_team']['name']} vs {match['away_team']['name']}"
            prediction_text = pred['prediction_value']
            confidence = pred['confidence']
            result = pred['result']
            
            # Status emoji
            if result == "PENDING":
                status_emoji = "⏳"
            elif result == "WON":
                status_emoji = "✅"
            elif result == "LOST":
                status_emoji = "❌"
            else:
                status_emoji = "➖"
            
            text += f"{status_emoji} <b>{match_text}</b>\n"
            text += f"   Prediction: {prediction_text}\n"
            text += f"   Confidence: {confidence:.0%}\n"
            text += f"   Status: {result}\n\n"
        
        # Add pagination if needed
        if len(predictions) == 10:
            text += "Use /my_predictions to see more..."
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in my_predictions command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load your predictions. Please try again later."
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    
    user = update.effective_user
    logger.info(f"Stats command from user {user.id}")
    
    try:
        # Get user stats
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if not telegram_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to register."
            )
            return
        
        stats = await user_service.get_user_stats(telegram_user['id'])
        
        # Format stats
        text = f"📊 <b>Your Prediction Statistics</b>\n\n"
        text += f"🎯 Total Predictions: {stats.get('total_predictions', 0)}\n"
        text += f"✅ Correct: {stats.get('correct_predictions', 0)}\n"
        text += f"❌ Incorrect: {stats.get('incorrect_predictions', 0)}\n"
        text += f"📈 Accuracy: {stats.get('accuracy', 0):.1f}%\n"
        text += f"🔥 Current Streak: {stats.get('current_streak', 0)}\n"
        text += f"🏆 Best Streak: {stats.get('longest_winning_streak', 0)}\n"
        text += f"📊 Global Rank: #{stats.get('global_rank', 'N/A')}\n"
        text += f"⭐ Total Points: {stats.get('total_points', 0)}\n"
        
        # Recent performance
        recent_accuracy = stats.get('recent_accuracy', 0)
        if recent_accuracy > 0:
            text += f"📈 Recent Form: {recent_accuracy:.1f}%\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load your statistics. Please try again later."
        )


async def predict_match_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle match prediction callback"""
    
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("predict_match_"):
        return
    
    match_id = int(query.data.split("_")[2])
    user = update.effective_user
    
    try:
        # Get match details
        match_service = MatchService()
        match = await match_service.get_match(match_id)
        
        if not match:
            await query.edit_message_text("❌ Match not found.")
            return
        
        # Check if user already predicted this match
        user_service = UserService()
        telegram_user = await user_service.get_telegram_user(user.id)
        
        if telegram_user:
            prediction_service = PredictionService()
            existing_prediction = await prediction_service.get_user_match_prediction(
                user_id=telegram_user['id'],
                match_id=match_id
            )
            
            if existing_prediction:
                await query.edit_message_text(
                    f"✅ You already predicted this match!\n\n"
                    f"Your prediction: {existing_prediction['prediction_value']}\n"
                    f"Confidence: {existing_prediction['confidence']:.0%}"
                )
                return
        
        # Create prediction options
        home_team = match['home_team']['name']
        away_team = match['away_team']['name']
        
        keyboard = [
            [
                InlineKeyboardButton(f"🏠 {home_team} Win", callback_data=f"pred_1_{match_id}"),
                InlineKeyboardButton("🤝 Draw", callback_data=f"pred_X_{match_id}"),
                InlineKeyboardButton(f"{away_team} Win 🏠", callback_data=f"pred_2_{match_id}")
            ],
            [
                InlineKeyboardButton("⚽ Over 2.5 Goals", callback_data=f"pred_O25_{match_id}"),
                InlineKeyboardButton("🔒 Under 2.5 Goals", callback_data=f"pred_U25_{match_id}")
            ],
            [
                InlineKeyboardButton("✅ Both Teams Score", callback_data=f"pred_BTTS_{match_id}"),
                InlineKeyboardButton("❌ Not Both Teams Score", callback_data=f"pred_NBTTS_{match_id}")
            ],
            [
                InlineKeyboardButton("🔙 Back to Matches", callback_data="predict")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
        date_str = match_date.strftime("%d/%m/%Y at %H:%M")
        
        text = f"🎯 <b>Make Your Prediction</b>\n\n"
        text += f"⚽ <b>{home_team} vs {away_team}</b>\n"
        text += f"📅 {date_str}\n"
        text += f"🏟️ {match.get('venue', 'TBD')}\n\n"
        text += f"Choose your prediction type:"
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in predict_match_callback: {e}")
        await query.edit_message_text("❌ Sorry, something went wrong.")


# Create handlers
prediction_handlers = [
    CommandHandler("predict", predict_command),
    CommandHandler("my_predictions", my_predictions_command),
    CommandHandler("stats", stats_command),
    CallbackQueryHandler(predict_match_callback, pattern="^predict_match_"),
    CallbackQueryHandler(predict_match_callback, pattern="^pred_"),
]