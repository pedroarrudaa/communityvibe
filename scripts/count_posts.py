#!/usr/bin/env python3
"""
Script to count and summarize posts in the database.
"""

import sys
import os
import logging
from sqlalchemy import func, text

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.post import Post, SentimentType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Count and summarize posts in the database"""
    db = SessionLocal()
    
    try:
        # Count total posts
        total_posts = db.query(func.count(Post.id)).scalar()
        logger.info(f"Total posts in database: {total_posts}")
        
        # Count posts by platform
        platform_counts = db.query(Post.platform, func.count(Post.id)).group_by(Post.platform).all()
        logger.info("Posts by platform:")
        for platform, count in platform_counts:
            logger.info(f"  - {platform}: {count}")
        
        # Count posts by source_name (subreddit)
        source_counts = db.query(Post.source_name, func.count(Post.id)).group_by(Post.source_name).all()
        logger.info("Posts by source:")
        for source, count in source_counts:
            logger.info(f"  - {source}: {count}")
        
        # Count posts by sentiment
        sentiment_counts = db.query(Post.sentiment, func.count(Post.id)).group_by(Post.sentiment).all()
        logger.info("Posts by sentiment:")
        for sentiment, count in sentiment_counts:
            sentiment_name = sentiment.value if sentiment else "None"
            logger.info(f"  - {sentiment_name}: {count}")
        
        # Count posts with categories - using raw SQL to avoid JSON comparison issues
        with_categories_result = db.execute(text(
            "SELECT COUNT(*) FROM posts WHERE categories IS NOT NULL AND categories::text != '[]'"
        )).scalar()
        logger.info(f"Posts with categories: {with_categories_result}")
        
        # Show recent posts
        logger.info("\nRecent posts (10):")
        recent_posts = db.query(Post).order_by(Post.created_at.desc()).limit(10).all()
        for post in recent_posts:
            logger.info(f"  - [ID: {post.id}] {post.content_text[:50]}... ({post.source_name})")
            if post.categories:
                logger.info(f"    Categories: {post.categories}, Sentiment: {post.sentiment}")
            else:
                logger.info(f"    Categories: None, Sentiment: {post.sentiment}")
        
        # Show posts with categories
        category_query = db.execute(text(
            "SELECT id, content_text, source_name, categories FROM posts WHERE categories IS NOT NULL AND categories::text != '[]' LIMIT 10"
        )).fetchall()
        logger.info("\nPosts with categories (10):")
        for row in category_query:
            logger.info(f"  - [ID: {row[0]}] {row[1][:50]}... ({row[2]})")
            logger.info(f"    Categories: {row[3]}")
        
    except Exception as e:
        logger.error(f"Error counting posts: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 