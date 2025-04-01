from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl
from app.models.post import PostStatus, SentimentType, CategoryType

class PostBase(BaseModel):
    platform: str
    platform_id: str
    platform_url: str
    author_username: Optional[str] = None
    author_platform_id: Optional[str] = None
    author_avatar_url: Optional[str] = None
    content_text: str
    source_type: str
    source_name: str

class PostCreate(PostBase):
    categories: Optional[List[str]] = []
    additional_data: Optional[Dict[str, Any]] = {}

class PostUpdate(BaseModel):
    sentiment: Optional[SentimentType] = None
    category: Optional[CategoryType] = None
    urgency: Optional[int] = None
    status: Optional[PostStatus] = None
    categories: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None
    openai_products: Optional[Dict[str, Any]] = None

class PostInDBBase(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    sentiment: Optional[SentimentType] = None
    category: Optional[CategoryType] = None
    urgency: Optional[int] = None
    status: PostStatus
    categories: List[str] = []
    extra_data: Dict[str, Any] = {}
    additional_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class Post(PostInDBBase):
    pass

class PostInDB(PostInDBBase):
    pass 