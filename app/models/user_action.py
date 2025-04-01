from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class ActionType(enum.Enum):
    VIEW = "VIEW"
    LIKE = "LIKE"
    SAVE = "SAVE"
    SHARE = "SHARE"
    REPORT = "REPORT"
    COMMENT = "COMMENT"
    FOLLOW = "FOLLOW"
    UNFOLLOW = "UNFOLLOW"
    MUTE = "MUTE"
    BLOCK = "BLOCK"

class UserAction(Base):
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(Enum(ActionType), nullable=False)
    action_metadata = Column(JSON, nullable=True)  # For storing additional action-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    post = relationship("Post", back_populates="user_actions")
    user = relationship("User", back_populates="actions")

    # Relationships will be defined in the Post model 