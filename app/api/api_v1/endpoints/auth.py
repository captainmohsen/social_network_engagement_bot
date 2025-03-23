from typing import Any
from jose import jwt
from pydantic import ValidationError
import json
from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.token_session import create_refresh_token
from app.core.config import settings
from app.models.user_session import UserSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis


from starlette.responses import Response

router = APIRouter()

@router.post("/refresh_token/", response_model=schemas.Token)
async def refresh_token(
    *,
    db: AsyncSession = Depends(deps.get_db),
    redis_conn: Redis = Depends(deps.get_redis_conn),
    refresh: schemas.token.RefreshToken
):
    refresh_token = refresh.model_dump()
    try:
        refresh_token = refresh_token["refresh_token"]
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        session_data = payload["session"]

        user_session: UserSession = (
            await db.execute(
                select(UserSession).where(UserSession.session_data == session_data)
            )
        ).scalars().first()

        if not user_session or user_session.is_revoked:
            raise Exception
    except (jwt.JWTError, ValidationError, Exception) as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await crud.user.get_by_id(db=db, user_id=user_session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User")

    token = await create_refresh_token(
        user=user,
        db=db,
        redis_conn=redis_conn,
        current_session=session_data,
    )
    return token


@router.post("/login/", name="auth:login")
async def login_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    redis_conn: Redis = Depends(deps.get_redis_conn),
    user_data: schemas.UserInput,
):
    user, login = await crud.user.authenticate(
        db, username=user_data.username, password=user_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password are incorrect",
        )
    elif not await crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    if login:
        token = await create_refresh_token(
            user=user,
            db=db,
            redis_conn=redis_conn,
        )
        return token
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User")


@router.post("/access_token/", name="auth:access_token")
async def login_user_access_token(
    *,
    db: AsyncSession = Depends(deps.get_db),
    redis_conn: Redis = Depends(deps.get_redis_conn),
    user_data: OAuth2PasswordRequestForm = Depends(),
):
    user, login = await crud.user.authenticate(
        db, username=user_data.username, password=user_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password are incorrect",
        )
    elif not await crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password are incorrect",
        )

    content = json.dumps(
        await create_refresh_token(
            user=user,
            db=db,
            redis_conn=redis_conn,
        ),
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
    ).encode("utf-8")
    return Response(content=content, status_code=200, media_type="application/json")


@router.post("/validate_token", response_model=schemas.User)
async def validate_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/logout/")
async def logout(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user_token: str = Depends(deps.get_current_user_token),
):
    payload = jwt.decode(
        current_user_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    session_data = payload["session"]
    user_session: UserSession = (
        await db.execute(select(UserSession).where(UserSession.session_data == session_data))
    ).scalars().first()

    return await crud.session.revoke_session(
        db=db, session_id=user_session.id, user_id=user_session.user_id
    )
