import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/communityvibe.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for different components
    logging.getLogger('app.services.openai_service').setLevel(logging.INFO)
    logging.getLogger('app.services.reddit_service').setLevel(logging.INFO)
    logging.getLogger('app.services.twitter_service').setLevel(logging.INFO)
    logging.getLogger('app.tasks').setLevel(logging.INFO)
    
    logging.info("Logging configured successfully") 