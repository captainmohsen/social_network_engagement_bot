from typing import Optional, List

from pydantic import BaseModel, UUID4


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    id: Optional[int] = None


class ValidationToken(BaseModel):
    verified: bool
    user_data: dict


class RefreshToken(BaseModel):
    refresh_token: str
