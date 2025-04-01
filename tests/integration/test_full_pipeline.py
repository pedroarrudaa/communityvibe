import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService, TwitterRateLimitError
from app.services.openai_service import OpenAIService
from app.services.keyword_service import KeywordService
from app.core.config import settings
from app.models.post import Post
from app.crud import post as post_crud
from app.crud import user as user_crud
from app.crud import user_action as user_action_crud
from app.schemas.user import UserCreate
from app.schemas.user_action import UserActionCreate
from app.schemas.post import PostCreate, PostUpdate
from app.models.user_action import ActionType

@pytest.fixture
def test_user(db_session: Session):
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        name="Test User",
        username="testuser"
    )
    return user_crud.create_user(db_session, user=user_in)

@pytest.mark.asyncio
async def test_reddit_data_collection(db_session: Session):
    """Test Reddit data collection and processing"""
    reddit_service = RedditService()
    openai_service = OpenAIService()
    
    # Fetch posts from a test subreddit
    posts = reddit_service.fetch_subreddit_posts("programming", limit=5)
    
    assert len(posts) > 0
    
    # Process and store posts
    for post_data in posts:
        # Create post
        db_post = post_crud.create_post(db_session, post_in=post_data)
        assert db_post is not None
        assert db_post.platform == "reddit"
        
        # Process with OpenAI
        sentiment_result = await openai_service.analyze_sentiment(db_post.content_text, [])
        assert sentiment_result is not None
        assert "sentiment" in sentiment_result
        
        # Update post with sentiment
        db_post = post_crud.update_post(
            db_session,
            db_obj=db_post,
            obj_in=PostUpdate(sentiment=sentiment_result["sentiment"])
        )
        assert db_post.sentiment == sentiment_result["sentiment"]

@pytest.mark.asyncio
async def test_twitter_data_collection(db_session: Session):
    """Test Twitter data collection and processing"""
    twitter_service = TwitterService()
    keyword_service = KeywordService()
    openai_service = OpenAIService()
    
    try:
        # Try to get real tweets first
        tweets = twitter_service.search_tweets(query="cursor", limit=10)
    except TwitterRateLimitError:
        # If we hit rate limit, use mock data
        tweets = [
            PostCreate(
                platform="twitter",
                platform_id="mock123",
                platform_url="https://twitter.com/mock_author/status/mock123",
                content_text="Just discovered the amazing cursor feature in VSCode! #coding #productivity",
                author_username="mock_author",
                source_type="twitter",
                source_name="twitter",
                categories=[],
                additional_data={}
            )
        ]
    
    assert len(tweets) > 0
    
    # Process tweets
    for tweet in tweets:
        # Initial keyword processing
        categories = keyword_service.categorize_text(tweet.content_text)
        assert len(categories) > 0, "No categories found for tweet content"
        assert "cursor" in categories, "Expected 'cursor' category to be found"
        
        # Create post
        db_post = post_crud.create_post(db_session, post_in=tweet)
        
        assert db_post is not None
        assert db_post.platform == "twitter"
        
        # Process with OpenAI
        sentiment_result = await openai_service.analyze_sentiment(db_post.content_text, [])
        assert sentiment_result is not None
        assert "sentiment" in sentiment_result

def test_user_actions(db_session: Session, test_user):
    """Test user action tracking"""
    # Create a test post
    post_data = PostCreate(
        platform="twitter",
        platform_id="test123",
        platform_url="https://twitter.com/test_author/status/test123",
        content_text="Test content",
        author_username="test_author",
        source_type="twitter",
        source_name="twitter",
        categories=[],
        additional_data={}
    )
    db_post = post_crud.create_post(db_session, post_in=post_data)
    
    # Create user actions
    actions = [
        {"action_type": ActionType.VIEW, "user_id": test_user.id, "post_id": db_post.id},
        {"action_type": ActionType.LIKE, "user_id": test_user.id, "post_id": db_post.id}
    ]
    
    for action_data in actions:
        action = user_action_crud.create(
            db_session,
            obj_in=UserActionCreate(**action_data)
        )
        assert action is not None
        assert action.user_id == test_user.id
        assert action.post_id == db_post.id
    
    # Verify action retrieval
    user_actions = user_action_crud.get_multi_by_user(
        db_session, user_id=test_user.id
    )
    assert len(user_actions) == 2

@pytest.mark.asyncio
async def test_post_processing_pipeline(db_session: Session):
    """Test the complete post processing pipeline"""
    # Create a test post without sentiment/categories
    post_data = PostCreate(
        platform="twitter",
        platform_id="test456",
        platform_url="https://twitter.com/test_author/status/test456",
        content_text="I absolutely love using VSCode for Python development! The integration with GitHub Copilot is amazing.",
        author_username="test_author",
        source_type="twitter",
        source_name="twitter",
        categories=[],
        additional_data={}
    )
    db_post = post_crud.create_post(db_session, post_in=post_data)
    
    # Process with keyword service
    keyword_service = KeywordService()
    categories = keyword_service.categorize_text(db_post.content_text)
    assert len(categories) > 0
    
    # Process with OpenAI
    openai_service = OpenAIService()
    
    # Sentiment analysis
    sentiment_result = await openai_service.analyze_sentiment(
        db_post.content_text,
        ["VSCode", "GitHub Copilot"]
    )
    assert sentiment_result is not None
    assert sentiment_result["sentiment"] == "positive"
    
    # Product extraction
    products = await openai_service.extract_products(db_post.content_text)
    assert any(p["name"] == "vs code" for p in products)
    
    # Convert products list to dictionary format
    products_dict = {
        "extracted_products": products,
        "confidence": 0.9,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Update post
    updated_post = post_crud.update_post(
        db_session,
        db_obj=db_post,
        obj_in=PostUpdate(
            sentiment=sentiment_result["sentiment"],
            categories=categories,
            openai_products=products_dict
        )
    )
    
    assert updated_post.sentiment == "positive"
    assert len(updated_post.categories) > 0
    assert any(p["name"] == "vs code" for p in updated_post.openai_products["extracted_products"]) 