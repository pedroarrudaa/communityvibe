from typing import List, Optional, Dict, Any
import tweepy
from app.core.config import settings
from app.schemas.post import PostCreate
from app.services.keyword_service import KeywordService
import logging
from datetime import datetime
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

class TwitterServiceError(Exception):
    """Base exception for Twitter service errors"""
    pass

class TwitterRateLimitError(TwitterServiceError):
    """Raised when Twitter API rate limit is exceeded"""
    pass

class TwitterService:
    def __init__(self):
        """Initialize the Twitter API client with credentials from settings"""
        self.client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_SECRET
        )
        self.keyword_service = KeywordService()
    
    def _get_fetch_limit(self, requested_limit: Optional[int] = None) -> int:
        """
        Determine the appropriate fetch limit based on development mode and requested limit
        """
        if requested_limit is not None:
            return min(requested_limit, 100)  # Twitter API limits to 100 per request
            
        if settings.DEV_MODE:
            logger.info(f"Development mode active. Limiting fetch to {settings.DEV_POST_LIMIT} tweets")
            return settings.DEV_POST_LIMIT
            
        return 100  # Default production limit
    
    def search_tweets(self, query: str, limit: int = 10) -> List[PostCreate]:
        """
        Search for tweets matching a query.
        
        Args:
            query: The search query
            limit: Maximum number of tweets to return
            
        Returns:
            List of PostCreate objects
        """
        try:
            # Get the actual fetch limit based on development mode
            fetch_limit = self._get_fetch_limit(limit)
            
            # Search tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=fetch_limit,
                tweet_fields=["author_id", "created_at", "entities"],
                expansions=["author_id"],
                user_fields=["username", "name", "profile_image_url"]
            )
            
            if not response.data:
                logger.warning(f"No tweets found for query: {query}")
                return []
            
            # Convert tweets to posts
            posts = []
            
            # Handle both real API response and mock response
            if hasattr(response, 'includes') and hasattr(response, 'data'):
                # Handle real API or mock response
                users = {}
                for user in response.includes.get("users", []):
                    user_id = user.id if hasattr(user, 'id') else user.get("id")
                    users[user_id] = user
                tweets = response.data
            else:
                # Handle dictionary response
                users = {user["id"]: user for user in response.get("includes", {}).get("users", [])}
                tweets = response.get("data", [])
            
            for tweet in tweets:
                try:
                    # Get the user data for this tweet
                    tweet_data = tweet._json if hasattr(tweet, '_json') else tweet
                    user_id = tweet_data.get("author_id")
                    if not user_id:
                        logger.warning(f"No author_id found in tweet {tweet_data.get('id')}")
                        continue
                        
                    user = users.get(user_id)
                    if not user:
                        logger.warning(f"User data not found for tweet {tweet_data.get('id')}")
                        continue
                    
                    # Convert tweet to post
                    user_data = user._json if hasattr(user, '_json') else user
                    post = self._convert_tweet_to_post(tweet=tweet_data, user=user_data)
                    posts.append(post)
                    
                except Exception as e:
                    logger.error(f"Error processing tweet {tweet_data.get('id')}: {str(e)}")
                    continue
            
            return posts
            
        except tweepy.TooManyRequests as e:
            logger.error(f"Error searching tweets: {str(e)}")
            if settings.DEV_MODE:
                logger.info("Development mode: returning mock data due to rate limit")
                return [
                    PostCreate(
                        platform="twitter",
                        platform_id="123456789",
                        platform_url="https://twitter.com/test_user/status/123456789",
                        content_text="Just started using Cursor IDE with AI features, it's amazing!",
                        author_username="test_user",
                        author_platform_id="987654321",
                        source_type="twitter",
                        source_name="twitter",
                        categories=[],
                        additional_data={}
                    )
                ]
            raise TwitterRateLimitError(str(e))
        except tweepy.TwitterServerError as e:
            logger.error(f"Twitter server error: {str(e)}")
            raise TwitterServiceError(f"Twitter server error: {str(e)}")
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            # For testing purposes, return mock data
            if settings.DEV_MODE:
                logger.info("Development mode: returning mock data")
                return [
                    PostCreate(
                        platform="twitter",
                        platform_id="123456789",
                        platform_url="https://twitter.com/test_user/status/123456789",
                        content_text="Just started using Cursor IDE with AI features, it's amazing!",
                        author_username="test_user",
                        author_platform_id="987654321",
                        source_type="twitter",
                        source_name="twitter",
                        categories=[],
                        additional_data={}
                    )
                ]
            raise TwitterServiceError(f"Error searching tweets: {str(e)}")
    
    def _convert_tweet_to_post(self, tweet: Dict[str, Any], user: Dict[str, Any]) -> PostCreate:
        """Convert a tweet to a PostCreate model"""
        try:
            # Extract tweet data
            tweet_id = str(tweet["id"])
            text = tweet["text"]
            author_id = str(tweet["author_id"])
            
            # Extract user data
            author_username = user["username"]
            author_name = user["name"]
            author_avatar_url = user.get("profile_image_url")
            
            # Extract URL
            tweet_url = f"https://twitter.com/{author_username}/status/{tweet_id}"
            if "entities" in tweet and "urls" in tweet["entities"]:
                for url in tweet["entities"]["urls"]:
                    if url["expanded_url"].startswith(f"https://twitter.com/{author_username}/status/"):
                        tweet_url = url["expanded_url"]
                        break
            
            # Create post data
            post_data = PostCreate(
                platform="twitter",
                platform_id=tweet_id,
                platform_url=tweet_url,
                content_text=text,
                author_username=author_username,
                author_platform_id=author_id,
                author_avatar_url=author_avatar_url,
                source_type="twitter",
                source_name="twitter",
                categories=[],
                additional_data={
                    "author_name": author_name,
                    "raw_tweet": tweet
                }
            )
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error converting tweet to post: {str(e)}")
            raise TwitterServiceError(f"Error converting tweet to post: {str(e)}") 