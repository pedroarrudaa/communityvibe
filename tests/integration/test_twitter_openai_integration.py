import pytest
from unittest.mock import patch, MagicMock
from app.services.twitter_service import TwitterService
from app.services.openai_service import OpenAIService
from app.models.post import Post
from datetime import datetime

@pytest.fixture
def twitter_service():
    return TwitterService()

@pytest.fixture
def openai_service():
    return OpenAIService()

@pytest.fixture
def mock_tweet():
    return {
        "data": [{
            "id": "123456789",
            "text": "Just started using Cursor IDE with AI features, it's amazing!",
            "created_at": datetime.now().isoformat(),
            "author_id": "987654321",
            "entities": {
                "urls": [
                    {
                        "url": "https://twitter.com/test_user/status/123456789",
                        "expanded_url": "https://twitter.com/test_user/status/123456789",
                        "display_url": "twitter.com/test_user/status/123456789"
                    }
                ]
            }
        }],
        "includes": {
            "users": [{
                "id": "987654321",
                "username": "test_user",
                "name": "Test User",
                "profile_image_url": "https://pbs.twimg.com/profile_images/test.jpg"
            }]
        }
    }

@pytest.fixture
def mock_user():
    return {
        "id": "987654321",
        "username": "test_user",
        "name": "Test User",
        "profile_image_url": "https://pbs.twimg.com/profile_images/test.jpg"
    }

@pytest.mark.asyncio
async def test_twitter_openai_integration(twitter_service, openai_service, mock_tweet):
    # Mock Twitter API response
    with patch('tweepy.Client.search_recent_tweets') as mock_search:
        mock_response = MagicMock()
        mock_response.data = mock_tweet["data"]
        mock_response.includes = mock_tweet["includes"]
        mock_search.return_value = mock_response
        
        # Mock OpenAI service
        with patch.object(openai_service, 'analyze_sentiment') as mock_analyze:
            mock_analyze.return_value = {
                "sentiment": "positive",
                "confidence": 0.95,
                "explanation": "User expresses enthusiasm about Cursor IDE and its AI features"
            }
            
            # Search tweets
            tweets = twitter_service.search_tweets(query="cursor", limit=10)  # Twitter API requires min 10
            
            # Assertions
            assert len(tweets) > 0
            assert tweets[0].content_text == mock_tweet["data"][0]["text"]
            assert tweets[0].author_username == mock_tweet["includes"]["users"][0]["username"]
            assert tweets[0].author_platform_id == mock_tweet["includes"]["users"][0]["id"]
            assert tweets[0].platform_url == mock_tweet["data"][0]["entities"]["urls"][0]["expanded_url"]
            
            # Analyze sentiment for the tweet
            sentiment_result = await openai_service.analyze_sentiment(
                tweets[0].content_text,
                ["Cursor IDE"]
            )
            
            # Verify OpenAI service was called
            mock_analyze.assert_called_once()
            call_args = mock_analyze.call_args[0]
            assert mock_tweet["data"][0]["text"] in call_args[0]  # content
            assert "Cursor IDE" in call_args[1]  # products 