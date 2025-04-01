from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user_action import UserAction, ActionType
from app.schemas.user_action import UserActionCreate, UserActionUpdate

class CRUDUserAction(CRUDBase[UserAction, UserActionCreate, UserActionUpdate]):
    def create_action(
        self, db: Session, *, user_id: int, post_id: int, action_type: ActionType, metadata: Optional[dict] = None
    ) -> UserAction:
        """Create a new user action"""
        db_obj = UserAction(
            user_id=user_id,
            post_id=post_id,
            action_type=action_type,
            metadata=metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserAction]:
        """Get all actions for a specific user"""
        return (
            db.query(UserAction)
            .filter(UserAction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_actions(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserAction]:
        """Get all actions for a specific user"""
        return (
            db.query(UserAction)
            .filter(UserAction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_post_actions(
        self, db: Session, *, post_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserAction]:
        """Get all actions for a specific post"""
        return (
            db.query(UserAction)
            .filter(UserAction.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_action_by_type(
        self, db: Session, *, user_id: int, post_id: int, action_type: ActionType
    ) -> Optional[UserAction]:
        """Get a specific action type for a user and post"""
        return (
            db.query(UserAction)
            .filter(
                UserAction.user_id == user_id,
                UserAction.post_id == post_id,
                UserAction.action_type == action_type
            )
            .first()
        )

    def remove_action(
        self, db: Session, *, user_id: int, post_id: int, action_type: ActionType
    ) -> Optional[UserAction]:
        """Remove a specific action"""
        obj = self.get_user_action_by_type(db, user_id=user_id, post_id=post_id, action_type=action_type)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

user_action = CRUDUserAction(UserAction) 