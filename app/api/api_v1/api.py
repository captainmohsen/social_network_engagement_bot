
from app.api.api_v1.endpoints import (auth, users,stats,track)

from fastapi import APIRouter

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(track.router, prefix="/tracks", tags=["tracks"])

api_router.include_router(stats.router, prefix="/stats", tags=["stats"])


