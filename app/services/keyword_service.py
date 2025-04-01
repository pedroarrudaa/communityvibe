import json
import os
import re
import logging
from typing import List, Dict, Set

# Configure logging
logger = logging.getLogger(__name__)

class KeywordService:
    def __init__(self):
        """Initialize the keyword service with categories and their keywords"""
        try:
            # Get the absolute path to the keywords.json file
            keywords_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "core", "keywords", "keywords.json"
            )
            
            # Load keywords from JSON file
            with open(keywords_path, 'r') as f:
                self.keywords_by_category = json.load(f)
                
            # Preprocess keywords for better matching (lowercase)
            for category, keywords in self.keywords_by_category.items():
                self.keywords_by_category[category] = [k.lower() for k in keywords]
                
            logger.info(f"Loaded keywords for {len(self.keywords_by_category)} categories")
        except Exception as e:
            logger.error(f"Error loading keywords: {str(e)}")
            # Fallback to empty keywords
            self.keywords_by_category = {
                "windsurf": [],
                "cursor": [],
                "lovable": [],
                "general": []
            }
    
    def categorize_text(self, text: str) -> List[str]:
        """
        Categorize a text based on keyword matches
        
        Args:
            text: The text to categorize
            
        Returns:
            A list of category names that match the text
        """
        if not text:
            return []
            
        text = text.lower()
        matched_categories = set()
        
        # Check each category's keywords
        for category, keywords in self.keywords_by_category.items():
            for keyword in keywords:
                # Use word boundary to match whole words
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    matched_categories.add(category)
                    break  # No need to check other keywords in this category
        
        return list(matched_categories)
    
    def get_available_categories(self) -> List[str]:
        """Get a list of all available categories"""
        return list(self.keywords_by_category.keys())
        
    def extract_products(self, text: str) -> List[str]:
        """
        Extract product mentions from text based on keywords.
        
        Args:
            text: The text to analyze
            
        Returns:
            A list of product names found in the text
        """
        if not text:
            return []
            
        text = text.lower()
        products = []
        
        # Check each category's keywords
        for category, keywords in self.keywords_by_category.items():
            for keyword in keywords:
                # Use word boundary to match whole words
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    products.append(keyword)
                    break  # No need to check other keywords in this category
        
        return products 