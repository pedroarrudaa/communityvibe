from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.user_action import ActionType

class UserActionBase(BaseModel):
    user_id: int
    post_id: int
    action_type: ActionType
    metadata: Optional[Dict[str, Any]] = None

class UserActionCreate(UserActionBase):
    pass

class UserActionUpdate(UserActionBase):
    pass

class UserActionInDBBase(UserActionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserAction(UserActionInDBBase):
    pass

class UserActionInDB(UserActionInDBBase):
    pass 