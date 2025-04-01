from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, cast, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import literal

from app.models.post import Post, PostStatus, SentimentType, CategoryType
from app.schemas.post import PostCreate, PostUpdate

def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

def get_post_by_platform_id(db: Session, platform_id: str) -> Optional[Post]:
    return db.query(Post).filter(Post.platform_id == platform_id).first()

def get_posts(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    platforms: Optional[List[str]] = None,
    sentiment: Optional[SentimentType] = None,
    category: Optional[CategoryType] = None,
    source_type: Optional[str] = None,
    source_name: Optional[str] = None,
    status: Optional[PostStatus] = None,
    keyword_category: Optional[str] = None
) -> List[Post]:
    query = db.query(Post)
    
    if platforms:
        query = query.filter(Post.platform.in_(platforms))
    if sentiment:
        query = query.filter(Post.sentiment == sentiment)
    if category:
        query = query.filter(Post.category == category)
    if source_type:
        query = query.filter(Post.source_type == source_type)
    if source_name:
        query = query.filter(Post.source_name == source_name)
    if status:
        query = query.filter(Post.status == status)
    
    # Get all posts first (regardless of keyword_category filter)
    posts = query.offset(skip).limit(limit).all()
    
    # If keyword_category is provided, filter in Python instead of SQL
    if keyword_category:
        # Manually filter posts that have the specified category in their categories array
        posts = [
            post for post in posts
            if post.categories and isinstance(post.categories, list) and keyword_category in post.categories
        ]
    
    return posts

def create_post(db: Session, *, post_in: PostCreate) -> Post:
    post = Post(
        platform=post_in.platform,
        platform_id=post_in.platform_id,
        platform_url=post_in.platform_url,
        author_username=post_in.author_username,
        author_platform_id=post_in.author_platform_id,
        author_avatar_url=post_in.author_avatar_url,
        content_text=post_in.content_text,
        source_type=post_in.source_type,
        source_name=post_in.source_name,
        categories=post_in.categories,
        additional_data=post_in.additional_data,
        status=PostStatus.NEW
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def update_post(
    db: Session,
    *,
    db_obj: Post,
    obj_in: PostUpdate
) -> Post:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Special handling for categories to merge and deduplicate
        if field == "categories" and value:
            # Get existing categories
            existing_categories = db_obj.categories or []
            # Merge with new categories and deduplicate
            updated_categories = list(set(existing_categories + value))
            setattr(db_obj, field, updated_categories)
        else:
            setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_post_categories(
    db: Session,
    *,
    db_obj: Post,
    categories: List[str]
) -> Post:
    """
    Update just the categories of a post, merging with existing categories
    """
    # Get existing categories
    existing_categories = db_obj.categories or []
    # Merge with new categories and deduplicate
    updated_categories = list(set(existing_categories + categories))
    db_obj.categories = updated_categories
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_post(db: Session, *, post_id: int) -> Post:
    obj = db.query(Post).get(post_id)
    db.delete(obj)
    db.commit()
    return obj

def get_posts_without_openai_analysis(
    db: Session,
    *,
    limit: int = 100,
    platforms: Optional[List[str]] = None
) -> List[Post]:
    """
    Get posts that haven't been analyzed by OpenAI yet.
    
    Args:
        db: Database session
        limit: Maximum number of posts to return
        platforms: Optional list of platforms to filter by
        
    Returns:
        List of posts that need OpenAI analysis
    """
    query = db.query(Post).filter(
        or_(
            Post.openai_analysis_timestamp.is_(None),
            Post.openai_sentiment.is_(None),
            Post.openai_products.is_(None),
            Post.openai_categories.is_(None)
        )
    )
    
    if platforms:
        query = query.filter(Post.platform.in_(platforms))
    
    return query.limit(limit).all()

def update_post_openai_analysis(
    db: Session,
    *,
    db_obj: Post,
    obj_in: PostUpdate
) -> Post:
    """
    Update a post with OpenAI analysis results.
    
    Args:
        db: Database session
        db_obj: The post to update
        obj_in: Update data containing OpenAI analysis results
        
    Returns:
        Updated post
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # Only update OpenAI-related fields
    openai_fields = [
        "openai_sentiment",
        "openai_products",
        "openai_categories",
        "openai_confidence",
        "openai_analysis_timestamp"
    ]
    
    for field in openai_fields:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj 