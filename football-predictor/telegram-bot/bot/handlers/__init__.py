"""
Setup all bot handlers
"""

from telegram.ext import Application

from .start import start_handler, help_handler
from .predictions import prediction_handlers
from .matches import match_handlers
from .user import user_handlers
from .admin import admin_handlers


def setup_handlers(application: Application):
    """Setup all bot handlers"""
    
    # Start and help handlers
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    
    # Prediction handlers
    for handler in prediction_handlers:
        application.add_handler(handler)
    
    # Match handlers
    for handler in match_handlers:
        application.add_handler(handler)
    
    # User handlers
    for handler in user_handlers:
        application.add_handler(handler)
    
    # Admin handlers
    for handler in admin_handlers:
        application.add_handler(handler)