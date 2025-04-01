from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.post import Post
from app.services.reddit_service import RedditService
from app.services.sentiment_service import SentimentService
from app.services.scheduler import IDE_SUBREDDITS, fetch_and_process_reddit_posts

router = APIRouter()

@router.post("/fetch/{subreddit}", response_model=dict)
async def fetch_subreddit_posts(
    subreddit: str,
    limit: int = 25,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch posts from a specific subreddit and store them in the database.
    """
    # Initialize services
    reddit_service = RedditService()
    sentiment_service = SentimentService()
    
    # Fetch posts
    try:
        posts = reddit_service.fetch_subreddit_posts(subreddit, limit)
        
        # Process and store posts
        saved_count = 0
        for post_schema in posts:
            # Check if post already exists
            existing_post = crud.post.get_post_by_platform_id(db, post_schema.platform_id)
            if existing_post:
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
            "message": f"Successfully fetched posts from r/{subreddit}",
            "fetched_count": len(posts),
            "saved_count": saved_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch posts from r/{subreddit}: {str(e)}"
        )

@router.post("/fetch-ide-subreddits", response_model=dict)
async def fetch_ide_subreddits(
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Trigger fetching of posts from all IDE-related subreddits.
    This runs the task in the background.
    """
    try:
        background_tasks.add_task(fetch_and_process_reddit_posts)
        return {
            "message": "Task started to fetch posts from IDE-related subreddits",
            "subreddits": IDE_SUBREDDITS
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start background task: {str(e)}"
        )

@router.get("/ide-subreddits", response_model=List[str])
async def get_ide_subreddits() -> Any:
    """
    Get the list of IDE-related subreddits being monitored.
    """
    return IDE_SUBREDDITS 