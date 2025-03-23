from typing import Optional
import re
from .BaseSchemaModel import BaseSchemaModel as BaseModel, DatabaseRequirementField
from pydantic import  ValidationInfo,field_validator, UUID4
from datetime import datetime
from uuid import UUID




# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str]

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str, info: ValidationInfo) -> str:
        pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.match(pat, v):
           return v
        else:
            print("Invalid Email")
            raise ValueError('Email is not valid')


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str, info: ValidationInfo) -> str:
        pat = r'(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$'
        if re.match(pat, v):
            return v
        else:
            print("Invalid Password")
            raise ValueError('Password format is not valid')

class UserInput(BaseModel):
    username: Optional[str] = None
    # email: Optional[str]= None
    password: Optional[str] = None

# Properties to receive via API on update
class UserUpdate(UserInput):
    password: Optional[str] = None


class UserInDBBase(UserBase,DatabaseRequirementField):
    id: Optional[UUID] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


    class Config:
        from_attributes = True



# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserRegisterResponse(BaseModel):
    phone_number: str

class ChangePassword(BaseModel):
    old_password: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str, info: ValidationInfo) -> str:
        pat = r'(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$'
        if re.match(pat, v):
            return v
        else:
            print("Invalid Password")
            raise ValueError('Password format is not valid')


class UserActiveInactive(BaseModel):
    is_active: Optional[bool] = None

