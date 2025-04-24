import uuid
from typing import Annotated

from pydantic import BaseModel
from pydantic.v1 import Field


class SuccessfulResponse(BaseModel):
    success: str = "ok"


class TokenData(BaseModel):
    uid: uuid.UUID | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserCreate(BaseModel):
    login: Annotated[str, Field(min_length=6, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=25)]


class UserLogin(BaseModel):
    login: Annotated[str, Field(min_length=6, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=25)]


class UserResponse(BaseModel):
    id: uuid.UUID
    login: Annotated[str, Field(min_length=6, max_length=50)]
