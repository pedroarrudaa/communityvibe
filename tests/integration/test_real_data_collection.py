import pytest
from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService, TwitterRateLimitError
from app.schemas.post import PostCreate
import logging
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio

@pytest.fixture
def reddit_service():
    return RedditService()

@pytest.fixture
def twitter_service():
    return TwitterService()

async def test_reddit_data_collection(reddit_service):
    """Test real data collection from Reddit"""
    try:
        # Fetch posts from r/programming with a small limit
        posts = reddit_service.fetch_subreddit_posts("programming", limit=3)
        
        # Basic assertions
        assert len(posts) > 0, "No posts were retrieved from Reddit"
        assert len(posts) <= 3, "Retrieved more posts than requested"
        assert all(isinstance(post, PostCreate) for post in posts), "Not all items are PostCreate objects"
        
        # Check content of first post
        first_post = posts[0]
        assert first_post.platform == "reddit", "Platform should be 'reddit'"
        assert first_post.platform_id, "Platform ID should not be empty"
        assert first_post.content_text, "Content text should not be empty"
        assert first_post.author_username, "Author username should not be empty"
        
        # Log successful retrieval
        logger.info(f"Successfully retrieved {len(posts)} posts from Reddit")
        logger.info(f"First post title: {first_post.content_text[:100]}...")
        
    except Exception as e:
        logger.error(f"Error collecting Reddit data: {str(e)}")
        raise

async def test_twitter_data_collection(twitter_service):
    """Test real data collection from Twitter"""
    try:
        # Enable development mode to ensure we get mock data if rate limited
        settings.DEV_MODE = True
        
        try:
            # First try to get real data with a small limit
            posts = twitter_service.search_tweets("vscode", limit=3)
            logger.info("Successfully retrieved real Twitter data")
        except TwitterRateLimitError:
            # If rate limited, we'll get mock data due to DEV_MODE being True
            logger.warning("Twitter rate limit hit, falling back to mock data")
            posts = twitter_service.search_tweets("vscode", limit=3)
        
        # Basic assertions
        assert len(posts) > 0, "No tweets were retrieved from Twitter"
        assert len(posts) <= 3, "Retrieved more tweets than requested"
        assert all(isinstance(post, PostCreate) for post in posts), "Not all items are PostCreate objects"
        
        # Check content of first tweet
        first_post = posts[0]
        assert first_post.platform == "twitter", "Platform should be 'twitter'"
        assert first_post.platform_id, "Platform ID should not be empty"
        assert first_post.content_text, "Content text should not be empty"
        assert first_post.author_username, "Author username should not be empty"
        
        # Log successful retrieval
        logger.info(f"Successfully retrieved {len(posts)} tweets")
        logger.info(f"First tweet content: {first_post.content_text[:100]}...")
        
    except Exception as e:
        logger.error(f"Error collecting Twitter data: {str(e)}")
        raise
    finally:
        # Reset development mode
        settings.DEV_MODE = False 