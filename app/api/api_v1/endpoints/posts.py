from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.post import Post, PostCreate, PostUpdate
from app.models.post import SentimentType, CategoryType, PostStatus
from app.services.keyword_service import KeywordService

router = APIRouter()

@router.get("/", response_model=List[Post])
def read_posts(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platforms: Optional[List[str]] = Query(None),
    sentiment: Optional[SentimentType] = None,
    category: Optional[CategoryType] = None,
    source_type: Optional[str] = None,
    source_name: Optional[str] = None,
    status: Optional[PostStatus] = None,
    keyword_category: Optional[str] = None,
) -> Any:
    """
    Retrieve posts with filters.
    
    - **platforms**: Filter by platform (e.g., reddit, twitter)
    - **sentiment**: Filter by sentiment type (positive, negative, neutral)
    - **category**: Filter by content category (bug, feature_request, etc.)
    - **source_type**: Filter by source type (reddit, forum, etc.)
    - **source_name**: Filter by source name (subreddit name, forum name, etc.)
    - **status**: Filter by post status (new, viewed, responded)
    - **keyword_category**: Filter by keyword category (windsurf, cursor, lovable, general)
    """
    # Validate keyword_category if provided
    if keyword_category:
        keyword_service = KeywordService()
        available_categories = keyword_service.get_available_categories()
        if keyword_category not in available_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid keyword_category. Available options: {', '.join(available_categories)}"
            )
    
    posts = crud.post.get_posts(
        db,
        skip=skip,
        limit=limit,
        platforms=platforms,
        sentiment=sentiment,
        category=category,
        source_type=source_type,
        source_name=source_name,
        status=status,
        keyword_category=keyword_category
    )
    
    # Initialize empty lists for categories if None
    for post in posts:
        if post.categories is None:
            post.categories = []
    
    return posts

@router.get("/categories", response_model=List[str])
def get_available_categories(
) -> Any:
    """
    Get a list of all available keyword categories.
    """
    keyword_service = KeywordService()
    return keyword_service.get_available_categories()

@router.post("/", response_model=Post)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: PostCreate,
) -> Any:
    """
    Create new post.
    """
    post = crud.post.create_post(db=db, post_in=post_in)
    return post

@router.get("/{post_id}", response_model=Post)
def read_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
) -> Any:
    """
    Get post by ID.
    """
    post = crud.post.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=Post)
def update_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    post_in: PostUpdate,
) -> Any:
    """
    Update post.
    """
    post = crud.post.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post = crud.post.update_post(db=db, db_obj=post, obj_in=post_in)
    return post

@router.delete("/{post_id}", response_model=Post)
def delete_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
) -> Any:
    """
    Delete post.
    """
    post = crud.post.get_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post = crud.post.delete_post(db=db, post_id=post_id)
    return post

@router.get("/debug/categories", response_model=dict)
def debug_categories(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Debug endpoint to show all posts with their categories.
    For development use only.
    """
    # Get all posts first
    all_posts = db.query(Post).all()
    
    # Filter in Python to avoid SQL errors
    posts_with_categories = []
    for post in all_posts:
        if post.categories and isinstance(post.categories, list) and len(post.categories) > 0:
            posts_with_categories.append(post)
    
    result = {
        "total_post_count": len(all_posts),
        "categorized_post_count": len(posts_with_categories),
        "posts_with_categories": []
    }
    
    for post in posts_with_categories:
        result["posts_with_categories"].append({
            "id": post.id,
            "platform": post.platform,
            "platform_id": post.platform_id,
            "categories": post.categories,
            "content_preview": post.content_text[:50] + "..." if post.content_text else None
        })
    
    return result

@router.get("/debug/filtered", response_model=List[Post])
def debug_filtered_posts(
    db: Session = Depends(deps.get_db),
    keyword_category: str = None,
) -> Any:
    """
    Debug endpoint to get posts filtered by keyword category.
    For development use only.
    """
    posts = crud.post.get_posts(
        db,
        limit=10,
        keyword_category=keyword_category
    )
    return posts 