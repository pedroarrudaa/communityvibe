from typing import Dict, Any, Optional, List
from app.models.post import SentimentType
from app.services.openai_service import OpenAIService
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        """Initialize the sentiment analysis service"""
        self.openai_service = OpenAIService()
    
    async def analyze_sentiment(self, content: str, products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment using OpenAI's GPT-4 model.
        
        Args:
            content: The text content to analyze
            products: Optional list of products to analyze sentiment for
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            # Get sentiment analysis from OpenAI
            result = await self.openai_service.analyze_sentiment(content, products)
            
            # Store the detailed analysis
            analysis = {
                "raw_result": result,
                "confidence": result.get("confidence", 0.0),
                "explanation": result.get("explanation", ""),
                "timestamp": datetime.now(timezone.utc)
            }
            
            # If products were provided, store product-specific sentiments
            if products and "product_sentiments" in result:
                analysis["product_sentiments"] = result["product_sentiments"]
            
            # Map the overall sentiment to our enum
            sentiment_str = result.get("overall_sentiment", result.get("sentiment", "neutral"))
            sentiment = SentimentType(sentiment_str.lower())
            
            return {
                "sentiment": sentiment,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # Return neutral sentiment in case of error
            return {
                "sentiment": SentimentType.NEUTRAL,
                "analysis": {
                    "error": str(e),
                    "confidence": 0.0,
                    "timestamp": datetime.now(timezone.utc)
                }
            } 