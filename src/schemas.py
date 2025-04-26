import datetime
import uuid
from typing import Optional, List

from pydantic import BaseModel
from src.models import Roles


class SuccessfulResponse(BaseModel):
    success: str = "ok"


class SemesterResponse(BaseModel):
    id: uuid.UUID
    name: str


class TransactionCreate(BaseModel):
    semester_id: uuid.UUID
    amount: float


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    semester_id: uuid.UUID
    amount: float
    comment: str
    created_at: datetime.datetime


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


class UserEdit(BaseModel):
    name: str
    surname: str
    patronymic: str
    phone: str


class UserLogin(BaseModel):
    login: str
    password: str
    role: Roles


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    group_id: Optional[uuid.UUID] = None
    role: Roles
    phone: str
    login: str
    transactions: List[TransactionResponse]


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    users: List[UserResponse]
