from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router, tags=["auth (v1)"])
api_v1_router.include_router(users_router, tags=["users (v1)"])
