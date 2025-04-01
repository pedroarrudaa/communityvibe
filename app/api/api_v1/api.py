from fastapi import APIRouter
from app.api.api_v1.endpoints import posts, reddit, twitter, users, user_actions

api_router = APIRouter()
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(reddit.router, prefix="/reddit", tags=["reddit"])
api_router.include_router(twitter.router, prefix="/twitter", tags=["twitter"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(user_actions.router, prefix="/user-actions", tags=["user-actions"]) 