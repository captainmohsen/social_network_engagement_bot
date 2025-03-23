from typing import Optional

from sqlalchemy import func, select
from app.crud.base import CRUDBase
from app.models.follower_history import FollowerHistory
from app.schemas.follower_history import FollowerHistoryCreate
from pydantic.types import UUID4
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDFollowerHistory(CRUDBase[FollowerHistory, FollowerHistoryCreate, FollowerHistoryCreate]):
    async def get_by_id(self, db: AsyncSession, *, follower_history_id: str) -> Optional[FollowerHistory]:
        result  = await db.execute(select(FollowerHistory).where(FollowerHistory.id == follower_history_id))
        return result.scalars().first()

    async def get_by_track_id(self, db: AsyncSession, *, track_id: str) -> Optional[FollowerHistory]:
        result = await db.execute(select(FollowerHistory).where(FollowerHistory.track_id == track_id))
        return result.scalars().first()


follower_history = CRUDFollowerHistory(FollowerHistory)
