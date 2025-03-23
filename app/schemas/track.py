from typing import Optional

from pydantic import ConfigDict, UUID4
from .BaseSchemaModel import BaseSchemaModel as BaseModel


# Shared properties
class TrackBase(BaseModel):
    social_media: Optional[str] = None
    profile_username: Optional[str] = None
    user_id: Optional[UUID4] = None
    alert_threshold: Optional[int] = None
    alert_enabled: Optional[bool] = None
    last_follower_count: Optional[int] = None



# Properties to receive via API on creation
class TrackCreate(BaseModel):
    social_media: Optional[str] = None
    profile_username: Optional[str] = None
    user_id: Optional[UUID4] = None


# Properties to receive via API on update
class TrackUpdate(BaseModel):
    alert_threshold: Optional[int] = None
    alert_enabled: Optional[bool] = None



class TrackResponse(TrackBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)

class TrackFollowerCountResponse(BaseModel):
    profile_username: Optional[str]
    last_follower_count: Optional[int]