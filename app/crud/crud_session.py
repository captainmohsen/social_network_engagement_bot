from typing import Any, Dict, Optional, Union

from app.models.user_session import UserSession
from app.schemas.user_session import UserSessionCreate
from app.crud.base import CRUDBase
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException,status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import exc as orm_exc


class CRUDSession(CRUDBase[UserSession, UserSessionCreate, None]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: str) -> Optional[UserSession]:
        result = await db.execute(select(UserSession).filter(UserSession.user_id == user_id))
        return result.scalars().first()

    async def get_by_session_data(self, db: AsyncSession, *, session_data: str) -> Optional[UserSession]:
        result = await db.execute(select(UserSession).filter(UserSession.session_data == session_data))
        return result.scalars().first()


    async def create(self, db: AsyncSession, *, obj_in: UserSessionCreate) -> UserSession:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            raise e

    async def revoke_session(self, db: AsyncSession, *, session_id: int, user_id: int) -> bool:
        try:
            result = await db.execute(select(UserSession).filter(UserSession.id == session_id))
            session = result.scalars().first()
            if session:
                if session.user_id != user_id:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="you don't have permission")

                session.is_revoked = True
                db.add(session)
                await db.commit()
                return True
            return False
        except orm_exc.NoResultFound:
            return False


session = CRUDSession(UserSession)