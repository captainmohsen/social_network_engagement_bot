import json
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException,status

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackUpdate
from app import crud




class CRUDTrack(CRUDBase[Track, TrackCreate, TrackUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: str) -> Optional[Track]:
        result = await db.execute(select(Track).where(Track.user_id == user_id))
        return result.scalars().all()

    async def get_by_profile_username(self, db: AsyncSession, *, profile_username: str) -> Optional[Track]:
        result = await db.execute(select(Track).where(Track.profile_username == profile_username))
        return result.scalars().first()

    async def get_by_track_id(
            self, db: AsyncSession, *, track_id: str
    ) -> Optional[Track]:
        result = await db.execute(select(Track).where(Track.id == track_id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: TrackCreate) -> Track:

        try:

            db_obj = Track(
                social_media=obj_in.social_media,
                profile_username=obj_in.profile_username,
                user_id=obj_in.user_id,
                alert_enabled=True,
            )

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=json.dumps(
                    {
                        "message": "Create profile and track has error",
                        "error": 'e',
                    }
                ),
            )






track = CRUDTrack(Track)
