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
    post_id = str(uuid.uuid4())
    return PostCreate(
        platform="reddit",
        platform_id=post_id,
        platform_url=f"https://reddit.com/r/programming/comments/{post_id}/mock_post",
        content_text="Just discovered VS Code's new AI features. The integration with GitHub Copilot is amazing for Python development!",
        author_username="test_user",
        author_platform_id=str(uuid.uuid4()),
        source_type="reddit",
        source_name="programming",
        categories=[],
        additional_data={"reddit": {"score": 4, "upvote_ratio": 0.83, "num_comments": 0}}
    )

def create_mock_twitter_post():
    """Create a mock Twitter post with unique IDs"""
    post_id = str(uuid.uuid4())
    return PostCreate(
        platform="twitter",
        platform_id=post_id,
        platform_url=f"https://twitter.com/test_user/status/{post_id}",
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
        # Convert posts to PostCreate objects with unique IDs
        post_objects = []
        for post in posts:
            post_id = str(uuid.uuid4())
            post_objects.append(PostCreate(
                platform="reddit",
                platform_id=post_id,
                platform_url=post.get("url", f"https://reddit.com/r/programming/comments/{post_id}/mock_post"),
                content_text=post.get("content_text", "No content"),
                author_username=post.get("author_username", "unknown"),
                author_platform_id=str(uuid.uuid4()),
                source_type="reddit",
                source_name="programming",
                categories=[],
                additional_data=post.get("additional_data", {})
            ))
        posts = post_objects
    except Exception as e:
        # Use mock data if Reddit API fails
        posts = [create_mock_reddit_post()]
    
    assert len(posts) > 0
    
    for post_data in posts:
        # Create post
        db_post = post_crud.create_post(db_session, post_in=post_data)
        
        try:
            # Process with OpenAI
            # 1. Extract products
            product_result = await openai_service.extract_products(db_post.content_text)
            if isinstance(product_result, dict):
                extracted_products = [p["name"] for p in product_result.get("products", [])]
            else:
                extracted_products = []
            
            # 2. Categorize content
            categories_result = await openai_service.categorize_content(
                content=db_post.content_text,
                available_categories=openai_service.supported_categories,
                products=extracted_products
            )
            
            # Verify the new categorization format
            assert "category" in categories_result
            assert categories_result["category"] in openai_service.supported_categories
            assert "confidence" in categories_result
            assert isinstance(categories_result["confidence"], float)
            assert "explanation" in categories_result
            assert isinstance(categories_result["explanation"], str)
            assert "secondary_categories" in categories_result
            assert isinstance(categories_result["secondary_categories"], list)
            
            # Print results for manual verification
            print(f"\nReddit Post Content: {db_post.content_text[:200]}...")
            print("Primary Category:", categories_result["category"])
            print("Secondary Categories:", categories_result["secondary_categories"])
            print("Confidence:", categories_result["confidence"])
            print("Explanation:", categories_result["explanation"])
            if extracted_products:
                print("Products:", extracted_products)
                print("Product Context:", categories_result.get("product_context", {}))
        
        except Exception as e:
            print(f"Error processing post {db_post.id}: {str(e)}")
            raise

@pytest.mark.asyncio
async def test_twitter_categorization(db_session):
    """Test categorization of real Twitter posts"""
    twitter_service = TwitterService()
    openai_service = OpenAIService()
    
    try:
        # Fetch 2 recent tweets about vscode
        tweets = twitter_service.search_tweets(query="vscode", limit=2)
        # Convert tweets to PostCreate objects with unique IDs
        tweet_objects = []
        for tweet in tweets:
            if isinstance(tweet, dict):
                post_id = str(uuid.uuid4())
                tweet_objects.append(PostCreate(
                    platform="twitter",
                    platform_id=post_id,
                    platform_url=f"https://twitter.com/test_user/status/{post_id}",
                    content_text=tweet.get("content_text", "No content"),
                    author_username=tweet.get("author_username", "unknown"),
                    author_platform_id=str(uuid.uuid4()),
                    source_type="twitter",
                    source_name="twitter",
                    categories=[],
                    additional_data=tweet.get("additional_data", {})
                ))
        tweets = tweet_objects if tweet_objects else [create_mock_twitter_post()]
    except TwitterRateLimitError:
        # Use mock data with unique IDs
        tweets = [create_mock_twitter_post()]
    
    assert len(tweets) > 0
    
    for tweet in tweets:
        # Create post
        db_post = post_crud.create_post(db_session, post_in=tweet)
        
        try:
            # Process with OpenAI
            # 1. Extract products
            product_result = await openai_service.extract_products(db_post.content_text)
            if isinstance(product_result, dict):
                extracted_products = [p["name"] for p in product_result.get("products", [])]
            else:
                extracted_products = []
            
            # 2. Categorize content
            categories_result = await openai_service.categorize_content(
                content=db_post.content_text,
                available_categories=openai_service.supported_categories,
                products=extracted_products
            )
            
            # Verify the new categorization format
            assert "category" in categories_result
            assert categories_result["category"] in openai_service.supported_categories
            assert "confidence" in categories_result
            assert isinstance(categories_result["confidence"], float)
            assert "explanation" in categories_result
            assert isinstance(categories_result["explanation"], str)
            assert "secondary_categories" in categories_result
            assert isinstance(categories_result["secondary_categories"], list)
            
            # Print results for manual verification
            print(f"\nTwitter Post Content: {db_post.content_text[:200]}...")
            print("Primary Category:", categories_result["category"])
            print("Secondary Categories:", categories_result["secondary_categories"])
            print("Confidence:", categories_result["confidence"])
            print("Explanation:", categories_result["explanation"])
            if extracted_products:
                print("Products:", extracted_products)
                print("Product Context:", categories_result.get("product_context", {}))
        
        except Exception as e:
            print(f"Error processing tweet {db_post.id}: {str(e)}")
            raise 