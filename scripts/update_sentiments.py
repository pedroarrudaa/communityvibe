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

from app.services.sentiment_service import SentimentService
from app.db.session import SessionLocal
from app import crud
from app.models.post import Post
import logging
from sqlalchemy.orm import Session
from app.schemas.post import PostUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_post_sentiments():
    """Update sentiment analysis for all posts in the database."""
    print("Starting sentiment analysis update for all posts...")
    
    # Create services
    sentiment_service = SentimentService()
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Get all posts
        posts = db.query(Post).all()
        
        print(f"Found {len(posts)} posts to analyze")
        
        # Update posts with sentiment analysis
        updated_count = 0
        for post in posts:
            try:
                # Analyze sentiment
                sentiment = sentiment_service.analyze_sentiment(post.content_text)
                print(f"Post {post.id}: {sentiment}")
                
                # Update post
                post.sentiment = sentiment
                db.add(post)
                updated_count += 1
                
                # Commit in batches to avoid memory issues
                if updated_count % 20 == 0:
                    db.commit()
                    print(f"Committed {updated_count} updates so far")
                
            except Exception as e:
                print(f"Error updating post {post.id}: {str(e)}")
        
        # Final commit
        db.commit()
        print(f"Updated sentiment for {updated_count} posts")
    
    except Exception as e:
        print(f"Error updating sentiments: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=== CommunityVibe Sentiment Update ===")
    update_post_sentiments()
    print("\nUpdate completed!") 