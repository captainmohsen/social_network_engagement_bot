import logging
from typing import Any
import redis
from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from fastapi import Body, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from sqlalchemy.orm import sessionmaker

from app.models.user_session import UserSession
import json
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, future=True, connect_args=settings.connect_args)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access_token/"
)


async def  get_db() -> AsyncGenerator[Any, Any, Any]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.close()



@asynccontextmanager
async def get_redis_conn() -> Redis:
    """
    Provides an async Redis connection using aioredis.
    """
    redis_conn = await Redis.from_url(f"redis://{settings.REDIS_SERVER}")
    try:
        yield redis_conn
    finally:
        await redis_conn.close()



def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        session_data = payload['session']
        try:
            redis_conn = redis.StrictRedis(host=settings.REDIS_HOST)
            user_data = redis_conn.get(session_data)
            if user_data is not None:
                return dict(verified=True, user_data=json.loads(user_data))
        finally:
            redis_conn.close()

        db = SessionLocal()
        user_session = db.query(UserSession) \
            .filter(UserSession.session_data == session_data).scalar()
        if not user_session:
            raise Exception('session not found')
        if user_session.is_revoked:
            raise Exception('session revoked')
        return dict(verified=True, user_data=crud.user.get_user_data(db=db, user_id=user_session.user_id))

    except (jwt.JWTError, Exception) as e:
        print(e)
        return dict(verified=False, user_data=None)


async def get_current_user_token(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    token_verify = verify_token(token)
    if not token_verify["verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await  crud.user.get(db, id=token_verify["user_data"]["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return token



async def get_current_user(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    token_verify = verify_token(token)
    if not token_verify["verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await crud.user.get(db, id=token_verify["user_data"]["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not await crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




