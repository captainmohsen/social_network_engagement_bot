from pydantic import ConfigDict, BaseModel,UUID4
from datetime import datetime
from typing import Optional



class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class DatabaseRequirementField(BaseSchemaModel):
    id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True



class DeleteResponse(BaseSchemaModel):
    result: bool