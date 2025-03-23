import json
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException,status

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func, select

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app import crud




class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_id(
            self, db: AsyncSession, *, user_id: str
    ) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:

        try:

            is_active = True
            db_obj = User(
                username=obj_in.username,
                is_active=is_active,
                hashed_password=get_password_hash(obj_in.password),
                email = obj_in.email,
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
                        "message": "The user with this username already exists in the system",
                        "error": 'e',
                    }
                ),
            )


    async def update(
            self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        from app.core.security import verify_password
        login = False
        user = await self.get_by_username(db, username=username)
        if not user:
            return None, login
        if not verify_password(password, user.hashed_password):
            return user, login
        login = True
        return user, login

    async def activate_inactivate(self, db: AsyncSession, *, user_id: str,is_active:bool) -> Optional[User]:
        user = await self.get_by_id(db, user_id=user_id)
        user.is_active = is_active
        db.add(user)
        await db.commit()
        return user


    async def is_active(self, user: User) -> bool:
        return user.is_active


    async def get_user_data(self,db: AsyncSession,user_id):
        user = await crud.user.get_by_id(db=db,user_id=user_id)
        return dict(
            id=user.id,
        )




user = CRUDUser(User)
