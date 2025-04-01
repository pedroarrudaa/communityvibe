from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from sqlalchemy.orm import Session
import asyncio

from app.db.session import SessionLocal
from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService
from app.services.openai_service import OpenAIService
from app.services.keyword_service import KeywordService
from app.api.api_v1.endpoints.twitter import IDE_KEYWORDS, fetch_ide_tweets_task
from app.core.config import settings
from app import crud
from app.tasks.post_processing import process_posts_with_openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of relevant subreddits
IDE_SUBREDDITS = [
    "programming",
    "vscode",
    "webdev",
    "ArtificialIntelligence",
    "javascript",
    "Python",
    "reactjs",
    "coding",
    "AItools",
]

def fetch_and_process_reddit_posts():
    """
    Fetch posts from relevant subreddits and store them in the database.
    Also perform keyword-based searches.
    """
    # Create a new DB session
    db = SessionLocal()
    
    try:
        # Initialize services
        reddit_service = RedditService()
        openai_service = OpenAIService()
        keyword_service = KeywordService()
        
        # Track statistics
        total_fetched = 0
        total_saved = 0
        total_updated = 0
        
        # Get available categories for keyword searches
        categories = keyword_service.get_available_categories()
        
        # Determine fetch limit based on development mode
        fetch_limit = settings.DEV_POST_LIMIT if settings.DEV_MODE else settings.MAX_POSTS_PER_FETCH
        logger.info(f"Running Reddit fetch task in {'development' if settings.DEV_MODE else 'production'} mode with limit {fetch_limit}")
        
        # Process each subreddit
        for subreddit in IDE_SUBREDDITS:
            try:
                # Step 1: Fetch new posts from the subreddit
                logger.info(f"Fetching posts from r/{subreddit}...")
                posts = reddit_service.fetch_subreddit_posts(subreddit, limit=fetch_limit)
                
                logger.info(f"Fetched {len(posts)} posts from r/{subreddit}")
                total_fetched += len(posts)
                
                # Process and store posts
                for post_schema in posts:
                    # Check if post already exists
                    existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
                    if existing_post:
                        # Update categories if necessary
                        if post_schema.categories:
                            crud.post.update_post_categories(db, db_obj=existing_post, categories=post_schema.categories)
                            total_updated += 1
                        continue
                        
                    # Create post first
                        post = crud.post.create_post(db, post_in=post_schema)
                        total_saved += 1
                
                # Step 2: Perform keyword searches for each category
                for category in categories:
                    # Get a sample keyword from the category to use for search
                    keyword_list = keyword_service.keywords_by_category.get(category, [])
                    if not keyword_list:
                        continue
                        
                    # Use first keyword for search
                    search_keyword = keyword_list[0]
                    
                    logger.info(f"Searching r/{subreddit} for '{search_keyword}' (category: {category})...")
                    search_posts = reddit_service.search_subreddit(subreddit, search_keyword, limit=fetch_limit)
                    
                    logger.info(f"Found {len(search_posts)} posts in r/{subreddit} for '{search_keyword}'")
                    total_fetched += len(search_posts)
                    
                    # Process and store search results
                    for post_schema in search_posts:
                        # Check if post already exists
                        existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
                        if existing_post:
                            # Update categories if necessary
                            if post_schema.categories:
                                crud.post.update_post_categories(db, db_obj=existing_post, categories=post_schema.categories)
                                total_updated += 1
                            continue
                            
                        # Create post
                            post = crud.post.create_post(db, post_in=post_schema)
                            total_saved += 1
                
            except Exception as e:
                logger.error(f"Error processing subreddit {subreddit}: {str(e)}")
                continue
                
        logger.info(f"Scheduled Reddit task completed. Fetched {total_fetched} posts, saved {total_saved} new posts, updated {total_updated} existing posts.")
    
    except Exception as e:
        logger.error(f"Error in scheduled Reddit task: {str(e)}")
    
    finally:
        db.close()

def fetch_and_process_twitter_posts():
    """
    Fetch tweets related to IDE keywords and store them in the database.
    """
    # Create a new DB session
    db = SessionLocal()
    
    try:
        # Determine fetch limit based on development mode
        fetch_limit = settings.DEV_POST_LIMIT if settings.DEV_MODE else settings.MAX_POSTS_PER_FETCH
        logger.info(f"Running Twitter fetch task in {'development' if settings.DEV_MODE else 'production'} mode with limit {fetch_limit}")
        
        # Execute the Twitter fetching task
        asyncio.run(fetch_ide_tweets_task(db))
        
    except Exception as e:
        logger.error(f"Error in scheduled Twitter task: {str(e)}")
    
    finally:
        db.close()

def start_scheduler():
    """
    Start the background scheduler for periodic tasks.
    """
    scheduler = None
    try:
        scheduler = BackgroundScheduler()
        
        # Schedule the Reddit post fetching task
        scheduler.add_job(
            fetch_and_process_reddit_posts,
            trigger=IntervalTrigger(hours=settings.REDDIT_FETCH_INTERVAL_HOURS),
            id="fetch_reddit_posts",
            name="Fetch Reddit Posts",
            replace_existing=True
        )
        
        # Schedule the Twitter post fetching task
        scheduler.add_job(
            fetch_and_process_twitter_posts,
            trigger=IntervalTrigger(hours=settings.TWITTER_FETCH_INTERVAL_HOURS),
            id="fetch_twitter_posts",
            name="Fetch Twitter Posts",
            replace_existing=True
        )
        
        # Schedule OpenAI post-processing
        scheduler.add_job(
            lambda: asyncio.run(process_posts_with_openai(SessionLocal())),
            trigger=IntervalTrigger(hours=settings.OPENAI_PROCESSING_INTERVAL_HOURS),
            id="process_posts_with_openai",
            name="Process Posts with OpenAI",
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info(f"Background scheduler started. Running in {'development' if settings.DEV_MODE else 'production'} mode.")
        logger.info(f"Reddit posts will be fetched every {settings.REDDIT_FETCH_INTERVAL_HOURS} hours.")
        logger.info(f"Twitter posts will be fetched every {settings.TWITTER_FETCH_INTERVAL_HOURS} hours.")
        logger.info(f"OpenAI post-processing will run every {settings.OPENAI_PROCESSING_INTERVAL_HOURS} hours.")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        if scheduler:
            scheduler.shutdown()
        raise 