import os
from dotenv import load_dotenv
from typing import Any, Dict, Optional
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "CommunityVibe"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Reddit API
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str

    # Twitter API
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_BEARER_TOKEN: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_SECRET: str

    # OpenAI API
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: int = 30
    OPENAI_MIN_CONFIDENCE: float = 0.7

    # Data Pipeline Settings
    REDDIT_FETCH_INTERVAL_HOURS: int = 1
    TWITTER_FETCH_INTERVAL_HOURS: int = 1
    OPENAI_PROCESSING_INTERVAL_HOURS: int = 2
    MAX_POSTS_PER_FETCH: int = 25
    MAX_POSTS_PER_OPENAI_BATCH: int = 5

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application Settings
    APP_NAME: str = "CommunityVibe"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Development Mode
    DEV_MODE: bool = True
    DEV_POST_LIMIT: int = 3

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Data Collection Settings
    REDDIT_POSTS_PER_FETCH: int = 10
    TWITTER_POSTS_PER_FETCH: int = 10

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 