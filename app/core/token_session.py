import json
import redis
import logging
from jose import jwt
from app.core.security import create_token
from app.api.deps import get_db
from app.api.deps import get_redis_conn
from app.core.config import settings
from app import crud
from app.models.user_session import UserSession
from app.models.user import User
import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession



logger = logging.getLogger(__name__)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        session_data = payload['session']

        redis_conn = await redis.from_url(f"redis://{settings.REDIS_SERVER}")
        try:
            user_data = await redis_conn.get(session_data)
            if user_data:
                return dict(verified=True, user_data=json.loads(user_data))
        finally:
            await redis_conn.close()

        async with get_db() as db:
            query = select(UserSession).where(UserSession.session_data == session_data)
            result = await db.execute(query)
            user_session: UserSession = result.scalar()

            if not user_session:
                raise Exception('Session not found')
            if user_session.is_revoked:
                raise Exception('Session revoked')

            return dict(
                verified=True,
                user_data=await crud.user.get_user_data(db=db, user_id=user_session.user_id)
            )

    except (jwt.JWTError, SQLAlchemyError, Exception) as e:
        logger.exception("Token verification failed")
        return dict(verified=False, user_data=None)


async def create_refresh_token(
    user: User,
    db: AsyncSession,
    redis_conn: redis.Redis,
    current_session: str = "",
) -> dict:
    """
    Creates a new access and refresh token pair for the user.
    """
    if current_session:  # When refreshing the token, reuse the current session
        user_session = await crud.session.get_by_session_data(db=db, session_data=current_session)
    else:
        user_session = await initiate_session(db=db, user=user)
        async with get_redis_conn() as redis_conn:
            await cache_user_data_for_session(db, redis_conn, user_session)

        # await cache_user_data_for_session(db=db, redis_conn=redis_conn, user_session=user_session)


    token = {
        "access_token":  create_token(
            user_session=user_session.session_data,
            user_id=str(user.id),
            email=user.email,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        "refresh_token":  create_token(
            user_session=user_session.session_data,
            user_id=str(user.id),
            email=user.email,
            expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        ),
        "session": user_session.session_data,
        "token_type": "bearer",
    }
    return token


async def initiate_session(db: AsyncSession, user: User) -> UserSession:
    sha_hash = hashlib.sha3_224()
    sha_hash.update(f"{datetime.utcnow()}{user.id}{secrets.token_urlsafe(16)}".encode())

    user_session = await crud.session.create(
        db=db, obj_in=dict(session_data=sha_hash.hexdigest(), user_id=user.id)
    )
    return user_session


async def cache_user_data_for_session(
    db: AsyncSession, redis_conn: redis.Redis, user_session: UserSession
) -> None:
    try:
        user_data = await crud.user.get_user_data(db=db, user_id=user_session.user_id)
        await redis_conn.set(
            name=user_session.session_data,
            value=json.dumps(user_data,default=str),
        )
    except Exception:
        logger.exception("User data save to Redis failed")
        if redis_conn:
            await redis_conn.close()


async def update_user_data_cache_for_user_sessions(
    db: AsyncSession, redis_conn: redis.Redis, user: User
):
    user_sessions = await crud.session.active_sessions(db=db, user_id=user.id)
    for session in user_sessions:
        try:
            user_data = await crud.user.get_user_data(db=db, user_id=session.user_id)
            await redis_conn.set(name=session.session_data, value=json.dumps(user_data))
        except Exception:
            logger.exception("User data save to Redis failed")

