import pytest
from app.services.reddit_service import RedditService
from app.services.twitter_service import TwitterService, TwitterRateLimitError
from app.services.openai_service import OpenAIService
from app.models.post import Post
from app.crud import post as post_crud
from app.schemas.post import PostCreate
from datetime import datetime
from app.db.session import SessionLocal
import uuid

@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_mock_reddit_post():
    """Create a mock Reddit post with unique IDs"""
    return PostCreate(
        platform="reddit",
        platform_id=str(uuid.uuid4()),
        platform_url=f"https://reddit.com/r/programming/comments/{uuid.uuid4()}/mock_post",
        content_text="Just discovered VS Code's new AI features. The integration with GitHub Copilot is amazing for Python development!",
        author_username="test_user",
        author_platform_id=str(uuid.uuid4()),
        source_type="reddit",
        source_name="programming",
        categories=[],
        additional_data={}
    )

def create_mock_twitter_post():
    """Create a mock Twitter post with unique IDs"""
    return PostCreate(
        platform="twitter",
        platform_id=str(uuid.uuid4()),
        platform_url=f"https://twitter.com/test_user/status/{uuid.uuid4()}",
        content_text="Just started using VS Code with GitHub Copilot, it's amazing! The AI features are really helping my productivity.",
        author_username="test_user",
        author_platform_id=str(uuid.uuid4()),
        source_type="twitter",
        source_name="twitter",
        categories=[],
        additional_data={}
    )

@pytest.mark.asyncio
async def test_reddit_categorization(db_session):
    """Test categorization of real Reddit posts"""
    reddit_service = RedditService()
    openai_service = OpenAIService()
    
    try:
        # Fetch 2 recent posts from r/programming
        posts = reddit_service.fetch_subreddit_posts("programming", limit=2)
    except Exception as e:
        # Use mock data if Reddit API fails
        posts = [create_mock_reddit_post()]
    
    assert len(posts) > 0
    
    for post_data in posts:
        # Ensure unique platform_id
        if isinstance(post_data, dict):
            post_data = PostCreate(
                platform="reddit",
                platform_id=str(uuid.uuid4()),
                platform_url=post_data.get("url", f"https://reddit.com/r/programming/comments/{uuid.uuid4()}/mock_post"),
                content_text=post_data.get("content_text", "No content"),
                author_username=post_data.get("author_username", "unknown"),
                author_platform_id=str(uuid.uuid4()),
                source_type="reddit",
                source_name="programming",
                categories=[],
                additional_data=post_data.get("additional_data", {})
            )
        
        # Create post
        db_post = post_crud.create_post(db_session, post_in=post_data)
        
        # Process with OpenAI
        # 1. Extract products
        product_result = await openai_service.extract_products(db_post.content_text)
        extracted_products = product_result if isinstance(product_result, list) else []
        
        # 2. Categorize content
        categories_result = await openai_service.categorize_content(
            content=db_post.content_text,
            available_categories=openai_service.supported_categories,
            products=[p["name"] for p in extracted_products] if extracted_products else []
        )
        
        # Verify categories - handle both response formats
        categories = (
            categories_result.get("overall_categories", []) 
            if "overall_categories" in categories_result 
            else categories_result.get("categories", [])
        )
        assert len(categories) > 0
        
        # Print results for manual verification
        print(f"\nReddit Post Content: {db_post.content_text[:200]}...")
        print("Categories:", categories)
        if extracted_products:
            print("Products:", [p["name"] for p in extracted_products])
            print("Product Categories:", categories_result.get("product_categories", {}))

@pytest.mark.asyncio
async def test_twitter_categorization(db_session):
    """Test categorization of real Twitter posts"""
    twitter_service = TwitterService()
    openai_service = OpenAIService()
    
    try:
        # Fetch 2 recent tweets about vscode
        tweets = twitter_service.search_tweets(query="vscode", limit=2)
    except TwitterRateLimitError:
        # Use mock data with unique IDs
        tweets = [create_mock_twitter_post()]
    
    assert len(tweets) > 0
    
    for tweet in tweets:
        # Create post
        db_post = post_crud.create_post(db_session, post_in=tweet)
        
        # Process with OpenAI
        # 1. Extract products
        product_result = await openai_service.extract_products(db_post.content_text)
        extracted_products = product_result if isinstance(product_result, list) else []
        
        # 2. Categorize content
        categories_result = await openai_service.categorize_content(
            content=db_post.content_text,
            available_categories=openai_service.supported_categories,
            products=[p["name"] for p in extracted_products] if extracted_products else []
        )
        
        # Verify categories - handle both response formats
        categories = (
            categories_result.get("overall_categories", []) 
            if "overall_categories" in categories_result 
            else categories_result.get("categories", [])
        )
        assert len(categories) > 0
        
        # Print results for manual verification
        print(f"\nTwitter Post Content: {db_post.content_text[:200]}...")
        print("Categories:", categories)
        if extracted_products:
            print("Products:", [p["name"] for p in extracted_products])
            print("Product Categories:", categories_result.get("product_categories", {})) 