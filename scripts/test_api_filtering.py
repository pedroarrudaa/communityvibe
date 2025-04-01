#!/usr/bin/env python3
"""
Script to test the API filtering by keyword category
"""

import sys
import os
import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"

def main():
    """Main function to test API filtering"""
    try:
        # Test getting available categories
        logger.info("Testing GET /posts/categories")
        response = requests.get(f"{API_BASE_URL}/posts/categories")
        response.raise_for_status()
        categories = response.json()
        logger.info(f"Available categories: {categories}")
        
        # Test filtering by each category
        for category in categories:
            logger.info(f"\nTesting GET /posts?keyword_category={category}")
            response = requests.get(f"{API_BASE_URL}/posts", params={"keyword_category": category, "limit": 3})
            
            if response.status_code == 200:
                posts = response.json()
                logger.info(f"Found {len(posts)} posts for category '{category}'")
                
                # Show brief details of each post
                for i, post in enumerate(posts):
                    logger.info(f"  Post {i+1}: {post['content_text'][:50]}...")
                    logger.info(f"    ID: {post['id']}, Categories: {post['categories']}")
            else:
                logger.error(f"Error filtering by category '{category}': {response.status_code} - {response.text}")
        
    except Exception as e:
        logger.error(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    main() 