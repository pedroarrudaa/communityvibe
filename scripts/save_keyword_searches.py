#!/usr/bin/env python3
"""
Script to perform keyword searches and save results to the database.
"""

import sys
import os
import logging
from sqlalchemy.orm import Session

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.reddit_service import RedditService
from app.services.sentiment_service import SentimentService
from app.services.keyword_service import KeywordService
from app import crud

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of subreddits to search
SUBREDDITS = [
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

def main():
    """Main function to perform keyword searches and save results"""
    # Create DB session
    db = SessionLocal()
    
    try:
        # Initialize services
        reddit_service = RedditService()
        sentiment_service = SentimentService()
        keyword_service = KeywordService()
        
        # Get available categories
        categories = keyword_service.get_available_categories()
        
        # Track statistics
        total_posts = 0
        total_saved = 0
        total_updated = 0
        
        # Process each subreddit
        for subreddit in SUBREDDITS:
            logger.info(f"Processing subreddit: r/{subreddit}")
            
            # Search for posts for each category
            for category in categories:
                # Get a sample keyword from the category to use for search
                keyword_list = keyword_service.keywords_by_category.get(category, [])
                if not keyword_list:
                    continue
                    
                # Use first keyword for search
                search_keyword = keyword_list[0]
                
                logger.info(f"  Searching for '{search_keyword}' (category: {category})...")
                search_posts = reddit_service.search_subreddit(subreddit, search_keyword, limit=10)
                
                logger.info(f"  Found {len(search_posts)} posts")
                total_posts += len(search_posts)
                
                # Process and store search results
                for post_schema in search_posts:
                    # Check if post already exists
                    existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
                    if existing_post:
                        # Update categories if necessary
                        if post_schema.categories:
                            crud.post.update_post_categories(db, db_obj=existing_post, categories=post_schema.categories)
                            logger.info(f"  Updated post: {existing_post.platform_id} (ID: {existing_post.id})")
                            total_updated += 1
                        continue
                        
                    # Analyze sentiment
                    try:
                        sentiment = sentiment_service.analyze_sentiment(post_schema.content_text)
                        post_schema_dict = post_schema.model_dump()
                        post_schema_dict["sentiment"] = sentiment
                        post = crud.post.create_post(db, post_in=post_schema)
                        logger.info(f"  Saved new post: {post.platform_id} (ID: {post.id})")
                        total_saved += 1
                    except Exception as e:
                        logger.error(f"  Error analyzing sentiment: {str(e)}")
                        # Continue even if sentiment analysis fails
                        post = crud.post.create_post(db, post_in=post_schema)
                        logger.info(f"  Saved new post without sentiment: {post.platform_id} (ID: {post.id})")
                        total_saved += 1
        
        logger.info(f"Completed keyword searches. Found {total_posts} posts, saved {total_saved} new posts, updated {total_updated} existing posts.")
        
        # Test filtering posts by category
        logger.info("\nVerifying database filtering by category:")
        for category in categories:
            posts = crud.post.get_posts(db, keyword_category=category, limit=5)
            logger.info(f"Found {len(posts)} posts in DB with category '{category}'")
            for post in posts[:3]:  # Show up to 3 examples
                logger.info(f"  - {post.content_text[:50]}...")
                
    except Exception as e:
        logger.error(f"Error performing keyword searches: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 