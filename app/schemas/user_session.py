from typing import Optional
from .BaseSchemaModel import BaseSchemaModel as BaseModel
from uuid import UUID


class UserSessionCreate(BaseModel):
    id: Optional[UUID] = None
    session_data: str
    user_id: Optional[UUID] = None


class UserSession(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None


    class Config:
        from_attributes = True

