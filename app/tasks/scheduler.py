from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
from app.core.config import settings
from app.tasks.post_processing import process_posts_with_openai
from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService
from app.db.session import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

def fetch_reddit_posts():
    """Fetch posts from Reddit periodically"""
    try:
        db = SessionLocal()
        reddit_service = RedditService()
        result = reddit_service.fetch_posts(db, limit=settings.REDDIT_POSTS_PER_FETCH)
        logger.info(f"Reddit posts fetched: {result}")
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {str(e)}")
    finally:
        db.close()

def fetch_twitter_posts():
    """Fetch posts from Twitter periodically"""
    try:
        db = SessionLocal()
        twitter_service = TwitterService()
        result = twitter_service.fetch_posts(db, limit=settings.TWITTER_POSTS_PER_FETCH)
        logger.info(f"Twitter posts fetched: {result}")
    except Exception as e:
        logger.error(f"Error fetching Twitter posts: {str(e)}")
    finally:
        db.close()

def process_posts():
    """Process posts with OpenAI periodically"""
    try:
        db = SessionLocal()
        result = process_posts_with_openai(db)
        logger.info(f"Posts processed with OpenAI: {result}")
    except Exception as e:
        logger.error(f"Error processing posts with OpenAI: {str(e)}")
    finally:
        db.close()

def main():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Add jobs
    scheduler.add_job(
        fetch_reddit_posts,
        trigger=IntervalTrigger(hours=1),
        id="Fetch Reddit Posts",
        name="Fetch Reddit Posts",
        next_run_time=datetime.now()
    )
    
    scheduler.add_job(
        fetch_twitter_posts,
        trigger=IntervalTrigger(hours=1),
        id="Fetch Twitter Posts",
        name="Fetch Twitter Posts",
        next_run_time=datetime.now()
    )
    
    scheduler.add_job(
        process_posts,
        trigger=IntervalTrigger(hours=2),
        id="Process Posts with OpenAI",
        name="Process Posts with OpenAI",
        next_run_time=datetime.now()
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Background scheduler started. Running in development mode.")
    logger.info("Reddit posts will be fetched every 1 hours.")
    logger.info("Twitter posts will be fetched every 1 hours.")
    logger.info("OpenAI post-processing will run every 2 hours.")
    
    try:
        # Keep the main thread alive
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete.")

if __name__ == "__main__":
    main() 