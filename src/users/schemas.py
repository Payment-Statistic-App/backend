import uuid
from typing import Optional

from pydantic import BaseModel
from src.users.models import Roles


class SuccessfulResponse(BaseModel):
    success: str = "ok"


class TokenData(BaseModel):
    uid: uuid.UUID | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    role: Roles
    phone: str
    login: str
    password: str


class UserLogin(BaseModel):
    login: str
    password: str
    role: Roles


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    group_id: Optional[uuid.UUID]
    role: Roles
    phone: str
    login: str
