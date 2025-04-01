from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import atexit
import logging

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.services.scheduler import start_scheduler
from app.core.logging_config import setup_logging

# Set up logging first
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CommunityVibe API",
    description="API for collecting and analyzing community feedback about development tools",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting CommunityVibe API")
    logger.info("OpenAI service configured for product identification")
    logger.info("Supported products: cursor, lovable, bolt, intellij, vs code, windsurf ide")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CommunityVibe API")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to CommunityVibe API"}

# Start the scheduler on application startup
scheduler = start_scheduler()

# Shut down the scheduler when the app is shutting down
atexit.register(lambda: scheduler.shutdown()) 