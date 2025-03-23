from fastapi import APIRouter,Depends,HTTPException,status
from app import models
from app.services.check_follower import FollowerChecker
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db,get_current_active_user


router = APIRouter()

@router.get("/top-follower-changes/")
async def get_top_follower_changes(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    hours: int = 24,
    top_n: int = 5):
    analysis = FollowerChecker()
    changes = await analysis.get_top_changes(hours=hours, top_n=top_n)
    return {"top_changes": changes}


@router.get("/engagement/{profile_username}")
async def get_engagement(
    profile_username: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    ):
    checker = FollowerChecker()
    engagement_rate = await checker.get_engagement(profile_username)

    if engagement_rate is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"profile_username": profile_username, "engagement_rate": engagement_rate}
