import uuid
from pydantic import BaseModel


class SuccessfulResponse(BaseModel):
    success: str = "ok"


class TokenData(BaseModel):
    uid: uuid.UUID | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class StudentCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    login: str
    password: str


class StudentLogin(BaseModel):
    login: str
    password: str


class StudentResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    login: str
