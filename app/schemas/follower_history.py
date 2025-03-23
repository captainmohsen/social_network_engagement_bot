from typing import Optional

from pydantic import ConfigDict, UUID4
from .BaseSchemaModel import BaseSchemaModel as BaseModel


# Shared properties
class FollowerHistoryBase(BaseModel):
    id: UUID4
    track_id: Optional[UUID4] = None
    follower_count: Optional[int] = None


# Properties to receive via API on creation
class FollowerHistoryCreate(BaseModel):
    track_id: Optional[UUID4] = None
    follower_count: Optional[int] = None



class FollowerHistoryResponse(FollowerHistoryBase):
    model_config = ConfigDict(from_attributes=True)

