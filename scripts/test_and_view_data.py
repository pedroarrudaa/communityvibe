#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Ensure we're using the correct Python environment
venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv")
site_packages = os.path.join(venv_path, "lib", "python3.9", "site-packages")
sys.path.insert(0, site_packages)

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.reddit_service import RedditService
from app.db.session import SessionLocal
from app import crud
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_save_posts():
    """Fetch posts from Reddit and save them to the database."""
    print("Starting to fetch posts from Reddit...")
    
    # Create services
    reddit_service = RedditService()
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Fetch posts from a subreddit
        subreddit = "programming"  # You can change this to any subreddit
        limit = 5
        
        print(f"Fetching {limit} posts from r/{subreddit}...")
        posts = reddit_service.fetch_subreddit_posts(subreddit, limit)
        
        print(f"Successfully fetched {len(posts)} posts")
        
        # Save posts to database
        saved_count = 0
        for post_schema in posts:
            # Check if post already exists
            existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
            if existing_post:
                print(f"Post {post_schema.platform_id} already exists. Skipping.")
                continue
            
            # Create post without sentiment analysis
            try:
                post = crud.post.create_post(db=db, post_in=post_schema)
                print(f"Saved post {post.id}: {post.content_text[:50]}...")
                saved_count += 1
            except Exception as e:
                print(f"Error saving post: {str(e)}")
        
        print(f"Saved {saved_count} new posts to database")
    
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
    
    finally:
        db.close()

def view_saved_posts():
    """View posts saved in the database."""
    print("\nViewing saved posts...")
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Get all posts
        posts = crud.post.get_posts(db)
        
        print(f"Found {len(posts)} posts in database")
        
        # Display posts
        for i, post in enumerate(posts):
            print(f"\nPost {i+1} (ID: {post.id}):")
            print(f"Platform: {post.platform} (Source: {post.source_type}/{post.source_name})")
            print(f"Author: {post.author_username}")
            print(f"Content: {post.content_text[:100]}...")
            print(f"URL: {post.platform_url}")
    
    except Exception as e:
        print(f"Error viewing posts: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=== CommunityVibe Data Test ===")
    fetch_and_save_posts()
    view_saved_posts()
    print("\nTest completed!") 