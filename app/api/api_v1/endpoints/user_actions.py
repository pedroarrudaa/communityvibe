from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_user_action
from app.models.user_action import ActionType
from app.schemas.user_action import UserAction, UserActionCreate

router = APIRouter()

@router.post("/", response_model=UserAction)
def create_user_action(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    post_id: int,
    action_type: ActionType,
    metadata: Optional[dict] = None
) -> UserAction:
    """
    Create a new user action.
    """
    try:
        return crud_user_action.user_action.create_action(
            db=db,
            user_id=user_id,
            post_id=post_id,
            action_type=action_type,
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating user action: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[UserAction])
def get_user_actions(
    user_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[UserAction]:
    """
    Get all actions for a specific user.
    """
    return crud_user_action.user_action.get_user_actions(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

@router.get("/post/{post_id}", response_model=List[UserAction])
def get_post_actions(
    post_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[UserAction]:
    """
    Get all actions for a specific post.
    """
    return crud_user_action.user_action.get_post_actions(
        db=db,
        post_id=post_id,
        skip=skip,
        limit=limit
    )

@router.get("/user/{user_id}/post/{post_id}/action/{action_type}", response_model=Optional[UserAction])
def get_user_action_by_type(
    user_id: int,
    post_id: int,
    action_type: ActionType,
    db: Session = Depends(deps.get_db)
) -> Optional[UserAction]:
    """
    Get a specific action type for a user and post.
    """
    return crud_user_action.user_action.get_user_action_by_type(
        db=db,
        user_id=user_id,
        post_id=post_id,
        action_type=action_type
    )

@router.delete("/user/{user_id}/post/{post_id}/action/{action_type}", response_model=Optional[UserAction])
def remove_user_action(
    user_id: int,
    post_id: int,
    action_type: ActionType,
    db: Session = Depends(deps.get_db)
) -> Optional[UserAction]:
    """
    Remove a specific action.
    """
    return crud_user_action.user_action.remove_action(
        db=db,
        user_id=user_id,
        post_id=post_id,
        action_type=action_type
    ) 