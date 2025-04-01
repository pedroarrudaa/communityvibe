import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app import crud
from app.services.openai_service import OpenAIService, OpenAIServiceError, OpenAIAnalysisError, OpenAITimeoutError
from app.schemas.post import PostUpdate
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

async def process_posts_with_openai(db: Session) -> Dict[str, Any]:
    """
    Process posts that haven't been analyzed by OpenAI.
    This includes sentiment analysis, product extraction, and categorization.
    Each post is processed once, with analysis performed for each mentioned product.
    
    Args:
        db: Database session
        
    Returns:
        dict: Statistics about the processing
    """
    try:
        # Initialize OpenAI service
        openai_service = OpenAIService()
        
        # Get posts without OpenAI analysis
        posts = crud.post.get_posts_without_openai_analysis(
            db,
            limit=settings.MAX_POSTS_PER_OPENAI_BATCH
        )
        
        if not posts:
            logger.info("No posts found that need OpenAI analysis")
            return {
                "processed_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "error_types": {},
                "error_messages": []
            }
        
        logger.info(f"Found {len(posts)} posts that need OpenAI analysis")
        
        # Track statistics
        processed_count = 0
        error_count = 0
        skipped_count = 0
        error_types = {}
        error_messages = []
        
        for post in posts:
            try:
                # Skip if post doesn't have content
                if not post.content_text:
                    logger.warning(f"Skipping post {post.id} - no content text")
                    skipped_count += 1
                    continue
                
                logger.info(f"Processing post {post.id} with OpenAI")
                
                # 1. Extract products first
                product_result = await openai_service.extract_products(post.content_text)
                extracted_products = [p["name"] for p in product_result.get("products", [])]
                
                # 2. Sentiment Analysis with product context
                sentiment_result = await openai_service.analyze_sentiment(
                    post.content_text,
                    products=extracted_products
                )
                
                # Default to neutral sentiment if confidence is low
                if sentiment_result.get("confidence", 0) < settings.OPENAI_MIN_CONFIDENCE:
                    sentiment_result["sentiment"] = "neutral"
                    for product in sentiment_result.get("product_sentiments", {}).values():
                        product["sentiment"] = "neutral"
                
                # 3. Content Categorization with product context
                categories_result = await openai_service.categorize_content(
                    post.content_text,
                    categories=openai_service.supported_categories,
                    products=extracted_products
                )
                
                # Prepare update data
                update_data = PostUpdate(
                    openai_sentiment=sentiment_result,
                    openai_products={
                        "extracted_products": product_result["products"],
                        "confidence": product_result["confidence"],
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    openai_categories=categories_result,
                    openai_analysis_timestamp=datetime.utcnow(),
                    openai_confidence=min(
                        sentiment_result.get("confidence", 0.0),
                        product_result.get("confidence", 0.0),
                        categories_result.get("confidence", 0.0)
                    )
                )
                
                # Update post with OpenAI analysis
                updated_post = crud.post.update_post_openai_analysis(
                    db,
                    db_obj=post,
                    obj_in=update_data
                )
                
                if updated_post:
                    processed_count += 1
                    logger.info(
                        f"Successfully processed post {post.id} with OpenAI - "
                        f"Found {len(extracted_products)} products"
                    )
                else:
                    error_count += 1
                    error_message = f"Failed to update post {post.id} with OpenAI analysis"
                    error_messages.append(error_message)
                    logger.error(error_message)
                
            except OpenAITimeoutError as e:
                error_count += 1
                error_types["timeout"] = error_types.get("timeout", 0) + 1
                error_messages.append(f"Timeout processing post {post.id}: {str(e)}")
                logger.error(f"Timeout processing post {post.id}: {str(e)}")
                continue
            except OpenAIAnalysisError as e:
                error_count += 1
                error_types["analysis"] = error_types.get("analysis", 0) + 1
                error_messages.append(f"Analysis error for post {post.id}: {str(e)}")
                logger.error(f"Analysis error for post {post.id}: {str(e)}")
                continue
            except OpenAIServiceError as e:
                error_count += 1
                error_types["service"] = error_types.get("service", 0) + 1
                error_messages.append(f"Service error for post {post.id}: {str(e)}")
                logger.error(f"Service error for post {post.id}: {str(e)}")
                continue
            except Exception as e:
                error_count += 1
                error_types["unexpected"] = error_types.get("unexpected", 0) + 1
                error_messages.append(f"Unexpected error processing post {post.id}: {str(e)}")
                logger.error(f"Unexpected error processing post {post.id}: {str(e)}")
                continue
        
        # Log final statistics
        logger.info(
            f"OpenAI post-processing completed. "
            f"Processed: {processed_count}, "
            f"Errors: {error_count}, "
            f"Skipped: {skipped_count}"
        )
        
        if error_types:
            logger.warning(f"Error types encountered: {error_types}")
        
        return {
            "processed_count": processed_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "error_types": error_types,
            "error_messages": error_messages
        }
        
    except Exception as e:
        error_message = f"Unexpected error in OpenAI post-processing task: {str(e)}"
        logger.error(error_message)
        return {
            "processed_count": 0,
            "error_count": 1,
            "skipped_count": 0,
            "error_types": {"unexpected": 1},
            "error_messages": [error_message]
        } 