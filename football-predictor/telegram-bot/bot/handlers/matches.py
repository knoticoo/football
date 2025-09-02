"""
Match information command handlers
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from services.match_service import MatchService
from services.league_service import LeagueService

logger = logging.getLogger(__name__)


async def fixtures_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fixtures command"""
    
    user = update.effective_user
    logger.info(f"Fixtures command from user {user.id}")
    
    try:
        # Get upcoming matches
        match_service = MatchService()
        matches = await match_service.get_upcoming_matches(limit=10)
        
        if not matches:
            await update.message.reply_text(
                "📅 No upcoming matches found.\n\n"
                "Check back later for new fixtures!"
            )
            return
        
        # Format fixtures
        text = "📅 <b>Upcoming Matches</b>\n\n"
        
        current_date = None
        for match in matches:
            match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
            date_str = match_date.strftime("%A, %d %B")
            time_str = match_date.strftime("%H:%M")
            
            # Add date header if new date
            if current_date != date_str:
                text += f"📅 <b>{date_str}</b>\n"
                current_date = date_str
            
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            league = match['league']['name']
            
            text += f"⚽ {home_team} vs {away_team}\n"
            text += f"   🕐 {time_str} | {league}\n\n"
        
        # Add league filter options
        keyboard = [
            [
                InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", callback_data="fixtures_league_39"),
                InlineKeyboardButton("🇪🇸 La Liga", callback_data="fixtures_league_140")
            ],
            [
                InlineKeyboardButton("🇩🇪 Bundesliga", callback_data="fixtures_league_78"),
                InlineKeyboardButton("🇮🇹 Serie A", callback_data="fixtures_league_135")
            ],
            [
                InlineKeyboardButton("🇫🇷 Ligue 1", callback_data="fixtures_league_61"),
                InlineKeyboardButton("🌍 All Leagues", callback_data="fixtures_all")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in fixtures command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load fixtures. Please try again later."
        )


async def standings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /standings command"""
    
    user = update.effective_user
    logger.info(f"Standings command from user {user.id}")
    
    try:
        # Get available leagues
        league_service = LeagueService()
        leagues = await league_service.get_leagues(limit=6)
        
        if not leagues:
            await update.message.reply_text(
                "📊 No league standings available right now."
            )
            return
        
        # Create league selection keyboard
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
            callback_data = f"standings_league_{league['id']}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🏆 <b>Select a League to View Standings</b>\n\n"
            "Choose from the available leagues:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in standings command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load standings. Please try again later."
        )


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /live command"""
    
    user = update.effective_user
    logger.info(f"Live command from user {user.id}")
    
    try:
        # Get live matches
        match_service = MatchService()
        live_matches = await match_service.get_live_matches()
        
        if not live_matches:
            await update.message.reply_text(
                "⚽ No live matches at the moment.\n\n"
                "Use /fixtures to see upcoming matches!"
            )
            return
        
        # Format live matches
        text = "🔴 <b>Live Matches</b>\n\n"
        
        for match in live_matches:
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            league = match['league']['name']
            status = match['status']
            
            # Status emoji
            status_emoji = "🔴" if status == "IN_PLAY" else "⏸️"
            
            text += f"{status_emoji} <b>{home_team} {home_score} - {away_score} {away_team}</b>\n"
            text += f"   📊 {league} | {status}\n\n"
        
        await update.message.reply_text(text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in live command: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't load live matches. Please try again later."
        )


async def fixtures_league_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle league fixtures callback"""
    
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("fixtures_league_"):
        return
    
    league_id = int(query.data.split("_")[2])
    
    try:
        # Get matches for specific league
        match_service = MatchService()
        matches = await match_service.get_upcoming_matches(league_id=league_id, limit=10)
        
        if not matches:
            await query.edit_message_text(
                "📅 No upcoming matches for this league."
            )
            return
        
        # Format fixtures
        text = f"📅 <b>Upcoming Matches</b>\n\n"
        
        current_date = None
        for match in matches:
            match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
            date_str = match_date.strftime("%A, %d %B")
            time_str = match_date.strftime("%H:%M")
            
            # Add date header if new date
            if current_date != date_str:
                text += f"📅 <b>{date_str}</b>\n"
                current_date = date_str
            
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            
            text += f"⚽ {home_team} vs {away_team}\n"
            text += f"   🕐 {time_str}\n\n"
        
        # Back button
        keyboard = [[InlineKeyboardButton("🔙 Back to All Fixtures", callback_data="fixtures_all")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in fixtures_league_callback: {e}")
        await query.edit_message_text("❌ Sorry, something went wrong.")


async def standings_league_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle league standings callback"""
    
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("standings_league_"):
        return
    
    league_id = int(query.data.split("_")[2])
    
    try:
        # Get league standings
        league_service = LeagueService()
        standings = await league_service.get_league_table(league_id)
        
        if not standings or not standings.get('standings'):
            await query.edit_message_text(
                "📊 Standings not available for this league."
            )
            return
        
        league_name = standings['league']['name']
        teams = standings['standings']
        
        # Format standings
        text = f"🏆 <b>{league_name} - Standings</b>\n\n"
        
        for i, team in enumerate(teams[:10], 1):  # Top 10 teams
            position = team.get('position', i)
            name = team['name']
            points = team.get('points', 0)
            played = team.get('matches_played', 0)
            wins = team.get('wins', 0)
            draws = team.get('draws', 0)
            losses = team.get('losses', 0)
            gd = team.get('goal_difference', 0)
            
            # Position emoji
            if position == 1:
                pos_emoji = "🥇"
            elif position == 2:
                pos_emoji = "🥈"
            elif position == 3:
                pos_emoji = "🥉"
            else:
                pos_emoji = f"{position}."
            
            text += f"{pos_emoji} <b>{name}</b>\n"
            text += f"   📊 {points}pts | {played} games | {wins}W-{draws}D-{losses}L | GD: {gd:+d}\n\n"
        
        # Back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Leagues", callback_data="standings_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in standings_league_callback: {e}")
        await query.edit_message_text("❌ Sorry, something went wrong.")


# Create handlers
match_handlers = [
    CommandHandler("fixtures", fixtures_command),
    CommandHandler("standings", standings_command),
    CommandHandler("live", live_command),
    CallbackQueryHandler(fixtures_league_callback, pattern="^fixtures_league_"),
    CallbackQueryHandler(standings_league_callback, pattern="^standings_league_"),
]