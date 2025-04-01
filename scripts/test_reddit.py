#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.reddit_service import RedditService
from app.core.config import settings

def test_reddit_connection():
    """Test connection to Reddit API and fetch some posts."""
    print("Testing Reddit API connection...")
    
    # Create Reddit service
    try:
        reddit_service = RedditService()
        print("✓ Successfully connected to Reddit API")
    except Exception as e:
        print(f"✗ Failed to connect to Reddit API: {e}")
        return
    
    # Test fetching posts from a subreddit
    subreddit = "python"  # A popular subreddit for testing
    limit = 5
    
    try:
        print(f"\nFetching {limit} posts from r/{subreddit}...")
        posts = reddit_service.fetch_subreddit_posts(subreddit, limit)
        
        print(f"✓ Successfully fetched {len(posts)} posts from r/{subreddit}\n")
        
        # Display the posts
        for i, post in enumerate(posts):
            print(f"Post {i+1}:")
            print(f"  Title: {post.content_text[:60]}{'...' if len(post.content_text) > 60 else ''}")
            print(f"  Author: {post.author_username}")
            print(f"  URL: {post.platform_url}")
            print()
            
    except Exception as e:
        print(f"✗ Failed to fetch posts from r/{subreddit}: {e}")

if __name__ == "__main__":
    test_reddit_connection() 