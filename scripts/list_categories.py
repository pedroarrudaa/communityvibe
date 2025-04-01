#!/usr/bin/env python3
"""
Script to directly check the categories of posts in the database.
"""

import sys
import os
import logging
from sqlalchemy.orm import Session
from pprint import pprint

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.post import Post
from app.services.keyword_service import KeywordService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to list posts by category"""
    # Create DB session
    db = SessionLocal()
    
    try:
        # Load available categories
        keyword_service = KeywordService()
        categories = keyword_service.get_available_categories()
        
        # Get all posts
        all_posts = db.query(Post).all()
        logger.info(f"Total posts in database: {len(all_posts)}")
        
        # Count posts by category
        categorized_posts = [p for p in all_posts if p.categories and isinstance(p.categories, list) and len(p.categories) > 0]
        logger.info(f"Posts with categories: {len(categorized_posts)}")
        
        # Show category distribution
        category_counts = {}
        for category in categories:
            posts_in_category = [p for p in categorized_posts if category in p.categories]
            category_counts[category] = len(posts_in_category)
            
        logger.info("Category distribution:")
        for category, count in category_counts.items():
            logger.info(f"  - {category}: {count} posts")
            
            # Show some examples for each category
            if count > 0:
                examples = [p for p in categorized_posts if category in p.categories][:3]
                for i, post in enumerate(examples):
                    logger.info(f"    Example {i+1}: {post.content_text[:50]}... (ID: {post.id}, Categories: {post.categories})")
        
        # Show some posts with multiple categories
        multi_category_posts = [p for p in categorized_posts if len(p.categories) > 1]
        logger.info(f"\nPosts with multiple categories: {len(multi_category_posts)}")
        for i, post in enumerate(multi_category_posts[:5]):
            logger.info(f"  Post {i+1}: {post.content_text[:50]}... (ID: {post.id}, Categories: {post.categories})")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 