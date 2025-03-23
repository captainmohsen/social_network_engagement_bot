from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db,get_current_active_user
from app.schemas.track import TrackResponse, TrackCreate,TrackUpdate,TrackFollowerCountResponse
from app.models.track import Track
from app.crud.crud_track import track
from app import models, schemas, crud
from app.schemas.search import FilterRuleType, Search, SearchResponse
from typing import Any
from fastapi.encoders import jsonable_encoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{track_id}", response_model=TrackResponse)
async def get_track_by_id(
    track_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),

) -> Track:
    """
    Get a track by its ID.
    """
    db_track = await track.get_by_track_id(db=db, track_id=track_id)
    if not db_track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="track not found")

    return db_track

@router.get("/", response_model=list[schemas.TrackResponse])
async def read_tracks(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tracks.
    """
    tracks = await crud.track.get_multi(db, skip=skip, limit=limit)

    return tracks




@router.post("/", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def create_track(
    track_in: TrackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Track:
    """
    Create a new track.
    """

    db_track = await track.create(db=db, obj_in=track_in)
    return db_track


@router.patch("/{track_id}/alert", response_model=TrackResponse, status_code=status.HTTP_200_OK)
async def update_alert_settings(
    track_id: str,
    track_in: TrackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),

) -> Track:
    """
    Update a track and set alert settings .
    """
    db_track = await track.get_by_track_id(db=db, track_id=track_id)
    if not db_track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="track not found")
    updated_track = await crud.track.update(db=db, db_obj=db_track, obj_in=track_in)
    return updated_track



@router.get("/followers/{profile_username}", response_model=TrackFollowerCountResponse, status_code=status.HTTP_201_CREATED)
async def get_follower_count(
    profile_username: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):


    track = crud.track.get_by_profile_username(db=db, profile_username=profile_username)

    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return track






@router.delete("/{track_id}", status_code=status.HTTP_200_OK)
async def delete_track(
    track_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a track by its ID.
    """
    db_track = await track.get_by_track_id(db=db, track_id=track_id)
    if not db_track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="track not found")
    await crud.track.remove(db=db, id=track_id)
