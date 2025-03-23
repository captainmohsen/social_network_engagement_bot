import logging
from typing import Any, Dict, List
import redis
from app import crud, models, schemas
from app.api import deps
from app.schemas.search import FilterRuleType, Search, SearchResponse
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

r = redis.Redis(host="redis")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    logger.info(users)

    return users


#
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in,role_name="CLIENT")
    return user



@router.put("/me", response_model=schemas.User)
async def update_user_me(
        *,
        db: AsyncSession = Depends(deps.get_db),
        password: str = Body(None),
        username: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if username is not None:
        user_in.username = username
    if email is not None:
        user_in.email = email
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{userId}", response_model=schemas.User)
async def read_user_by_id(
        userId: str,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, id=userId)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user) or not crud.user.is_chatbotuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{userId}", response_model=schemas.User)
async def update_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        userId: str,
        userIn: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get_by_id(db, user_id=userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )
    if not userIn.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided to update the user.",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=userIn)
    return user

@router.patch("/{userId}", response_model=schemas.User)
async def active_inactive_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        userId: str,
        userIn: schemas.UserActiveInactive,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Active or Inactive a user.
    """
    user = await crud.user.get_by_id(db, user_id=userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )

    updated_user = await crud.user.activate_inactivate(db, user_id=userId, is_active=userIn.is_active)

    return updated_user



@router.delete("/{user_id}")
async def delete_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_id: str,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete one user by  id.
    """

    user = await crud.user.get_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with this id not found")

    l_activity = await crud.login_activity.get_by_user_id(db=db, user_id=user.id)

    session = await crud.session.get_by_user_id(db=db, user_id=user.id)


    try:
        if l_activity:
            activity = await crud.login_activity.remove(db=db, id=l_activity.id)
            await db.delete(activity)
        if session:
            user_session = await crud.session.remove(db=db, id=session.id)
            await db.delete(user_session)
        user_r = await crud.user.remove(db=db, id=user.id)
        await db.delete(user_r)
        await db.commit()


    except Exception as e:
        raise   HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



    return {"message": "remove user done  successfully..."}




@router.post("/search", response_model=SearchResponse[schemas.UserInDB])
async def search_user(
        *, db: AsyncSession = Depends(deps.get_db), search_params: Search,
        current_user: models.User = Depends(deps.get_current_user),

) -> Any:
    """
    Search in users.
    """
    try:
        rules: Dict[FilterRuleType] = jsonable_encoder(search_params)["filter"]

        total, users = await crud.user.search(
            db,
            rules=rules,
            page_number=search_params.page_number,
            page_size=search_params.page_size,
            item_sort=search_params.item_sort,
            direction_sort=search_params.direction_sort
        )

        return SearchResponse[schemas.UserInDB](result=users, total=total)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


