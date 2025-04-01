#!/usr/bin/env python3
"""
Test script for keyword categorization.
This script fetches posts from Reddit, categorizes them using keywords,
and displays the results.
"""

import sys
import os
import logging
from sqlalchemy.orm import Session
from pprint import pprint

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.reddit_service import RedditService
from app.services.keyword_service import KeywordService
from app import crud

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to test keyword categorization"""
    # Create DB session
    db = SessionLocal()
    
    try:
        # Initialize services
        reddit_service = RedditService()
        keyword_service = KeywordService()
        
        # Display available categories and their keywords
        logger.info("Available keyword categories:")
        for category, keywords in keyword_service.keywords_by_category.items():
            logger.info(f"  - {category}: {', '.join(keywords[:3])}... ({len(keywords)} keywords)")
        
        # Fetch a small number of posts from a programming-related subreddit
        subreddit = "programming"
        limit = 10
        logger.info(f"Fetching {limit} posts from r/{subreddit}...")
        
        posts = reddit_service.fetch_subreddit_posts(subreddit, limit)
        logger.info(f"Fetched {len(posts)} posts")
        
        # Display each post and its categorization
        for i, post in enumerate(posts):
            logger.info(f"\nPost {i+1}/{len(posts)}")
            logger.info(f"Title: {post.content_text[:100]}...")
            logger.info(f"Categories: {post.categories}")
            
            # Check if post already exists in DB
            existing_post = crud.post.get_post_by_platform_id(db, post.platform_id)
            if existing_post:
                logger.info(f"Post already exists in DB (ID: {existing_post.id})")
                
                # Update categories if needed
                if post.categories:
                    crud.post.update_post_categories(db, db_obj=existing_post, categories=post.categories)
                    logger.info(f"Updated categories: {existing_post.categories}")
            else:
                logger.info("Post does not exist in DB")
        
        # Test keyword search functionality
        for category in keyword_service.get_available_categories():
            # Skip if no keywords for this category
            keywords = keyword_service.keywords_by_category.get(category, [])
            if not keywords:
                continue
                
            # Use first keyword for search
            search_keyword = keywords[0]
            
            logger.info(f"\nSearching r/{subreddit} for '{search_keyword}' (category: {category})...")
            search_posts = reddit_service.search_subreddit(subreddit, search_keyword, limit=3)
            
            logger.info(f"Found {len(search_posts)} posts for keyword '{search_keyword}'")
            for i, post in enumerate(search_posts):
                logger.info(f"  Post {i+1}: {post.content_text[:100]}...")
                logger.info(f"  Categories: {post.categories}")
        
        # Test filtering posts by category
        logger.info("\nTesting database filtering by category:")
        for category in keyword_service.get_available_categories():
            posts = crud.post.get_posts(db, keyword_category=category, limit=5)
            logger.info(f"Found {len(posts)} posts in DB with category '{category}'")
            
    except Exception as e:
        logger.error(f"Error testing keyword categorization: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 