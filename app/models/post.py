from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class PostStatus(str, enum.Enum):
    NEW = "new"
    VIEWED = "viewed"
    RESPONDED = "responded"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class CategoryType(str, enum.Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    DISCUSSION = "discussion"
    FEEDBACK = "feedback"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)  # reddit, twitter, etc.
    platform_id = Column(String, unique=True, nullable=False)
    platform_url = Column(String, nullable=False)
    
    # Author information
    author_username = Column(String)
    author_platform_id = Column(String)
    author_avatar_url = Column(String)
    
    # Content
    content_text = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Source information
    source_type = Column(String, nullable=False)  # forum, reddit, twitter
    source_name = Column(String, nullable=False)  # specific forum name, subreddit, etc.
    
    # Metadata
    sentiment = Column(Enum(SentimentType))
    category = Column(Enum(CategoryType))
    urgency = Column(Integer, default=0)
    
    # New field for keyword-based categories (windsurf, cursor, lovable, general)
    categories = Column(JSON, default=[])
    
    # Engagement
    status = Column(Enum(PostStatus), default=PostStatus.NEW)
    
    # Additional metadata stored as JSON
    extra_data = Column(JSON, default={})
    
    # Raw API response data stored as JSON
    additional_data = Column(JSON, default={})
    
    # OpenAI Analysis Results
    openai_sentiment = Column(JSON, default={})  # Stores detailed sentiment analysis
    openai_products = Column(JSON, default={})   # Stores product mentions and analysis
    openai_categories = Column(JSON, default={}) # Stores detailed categorization
    openai_confidence = Column(Float)             # Overall confidence score
    openai_analysis_timestamp = Column(DateTime(timezone=True))  # When the analysis was performed
    
    # Relationships
    user_actions = relationship("UserAction", back_populates="post", cascade="all, delete-orphan") 