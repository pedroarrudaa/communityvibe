from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.post import Post
from app.services.twitter_service import TwitterService
from app.services.sentiment_service import SentimentService

router = APIRouter()

# List of relevant Twitter search keywords
IDE_KEYWORDS = [
    "cursor code editor",
    "windsurf IDE",
    "coding IDE",
    "AI programming tools",
    "Python IDE",
    "JavaScript editor",
    "VSCode alternative",
    "programming tools",
    "code IDE",
    "software development environment"
]

@router.post("/search", response_model=dict)
async def search_tweets(
    query: str,
    limit: int = 25,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Search for tweets using a keyword or phrase
    """
    # Initialize services
    twitter_service = TwitterService()
    sentiment_service = SentimentService()
    
    # Search tweets
    try:
        posts = twitter_service.search_tweets(query, limit)
        
        # Process and store tweets
        saved_count = 0
        updated_count = 0
        for post_schema in posts:
            # Check if post already exists
            existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
            if existing_post:
                # Update categories if necessary
                if post_schema.categories:
                    crud.post.update_post_categories(db, db_obj=existing_post, categories=post_schema.categories)
                    updated_count += 1
                continue
                
            # Analyze sentiment
            try:
                sentiment = sentiment_service.analyze_sentiment(post_schema.content_text)
                post_data = post_schema.model_dump()
                post_data["sentiment"] = sentiment
                post = crud.post.create_post(db, post_in=post_schema)
                saved_count += 1
            except Exception as e:
                # Continue even if sentiment analysis fails
                post = crud.post.create_post(db, post_in=post_schema)
                saved_count += 1
        
        return {
            "message": f"Successfully searched tweets for '{query}'",
            "found_count": len(posts),
            "saved_count": saved_count,
            "updated_count": updated_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search tweets: {str(e)}"
        )

@router.post("/fetch-ide-tweets", response_model=dict)
async def fetch_ide_tweets(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Trigger fetching of tweets related to IDE keywords
    """
    try:
        background_tasks.add_task(fetch_ide_tweets_task, db)
        return {
            "message": "Task started to fetch tweets related to IDE keywords",
            "keywords": IDE_KEYWORDS
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start background task: {str(e)}"
        )

@router.get("/ide-keywords", response_model=List[str])
async def get_ide_keywords() -> Any:
    """
    Get the list of IDE-related keywords being monitored for Twitter searches
    """
    return IDE_KEYWORDS

async def fetch_ide_tweets_task(db: Session):
    """
    Background task to fetch tweets for all IDE keywords
    """
    twitter_service = TwitterService()
    sentiment_service = SentimentService()
    
    total_fetched = 0
    total_saved = 0
    total_updated = 0
    
    for keyword in IDE_KEYWORDS:
        try:
            # Fetch tweets for this keyword
            posts = twitter_service.search_tweets(keyword, limit=25)
            total_fetched += len(posts)
            
            # Process and store tweets
            for post_schema in posts:
                # Check if post already exists
                existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
                if existing_post:
                    # Update categories if necessary
                    if post_schema.categories:
                        crud.post.update_post_categories(db, db_obj=existing_post, categories=post_schema.categories)
                        total_updated += 1
                    continue
                    
                # Analyze sentiment
                try:
                    sentiment = sentiment_service.analyze_sentiment(post_schema.content_text)
                    post_data = post_schema.model_dump()
                    post_data["sentiment"] = sentiment
                    post = crud.post.create_post(db, post_in=post_schema)
                    total_saved += 1
                except Exception as e:
                    # Continue even if sentiment analysis fails
                    post = crud.post.create_post(db, post_in=post_schema)
                    total_saved += 1
                    
        except Exception as e:
            import logging
            logging.error(f"Error fetching tweets for keyword '{keyword}': {str(e)}")
            continue
    
    import logging
    logging.info(f"Twitter fetch task completed. Fetched {total_fetched} tweets, saved {total_saved} new tweets, updated {total_updated} existing tweets.") 