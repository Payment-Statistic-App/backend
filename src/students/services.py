import uuid
import jwt

from datetime import timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config_data.config import Config, load_config
from utils.auth_settings import validate_password, decode_jwt, encode_jwt

from src.students.models import Student
from src.students.repositories import StudentRepository
from src.students.schemas import StudentCreate, TokenData, StudentLogin
from src.students.exceptions import CredentialException, TokenTypeException, NotFoundException, LoginExistsException

http_bearer = HTTPBearer()

settings: Config = load_config(".env")
auth_config = settings.authJWT

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class StudentService:
    repository = StudentRepository()

    @staticmethod
    def create_jwt(
            token_type: str,
            token_data: dict,
            expire_minutes: int = auth_config.access_token_expire_minutes,
            expire_timedelta: timedelta | None = None
    ) -> str:
        jwt_payload = {TOKEN_TYPE_FIELD: token_type}
        jwt_payload.update(token_data)
        token = encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta
        )
        return token

    def create_access_token(self, student: Student) -> str:
        jwt_payload = {
            "sub": str(student.id),
            "login": student.login,
        }
        return self.create_jwt(
            token_type=ACCESS_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_minutes=auth_config.access_token_expire_minutes
        )

    def create_refresh_token(self, student: Student) -> str:
        jwt_payload = {
            "sub": str(student.id),
            "login": student.login,
        }
        return self.create_jwt(
            token_type=REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=auth_config.refresh_token_expire_days)
        )

    async def authenticate_student(self, student_data: StudentLogin) -> Optional[Student]:
        student = await self.repository.get_student_by_login(student_data.login)
        if not student:
            raise CredentialException()
        if not validate_password(student_data.password, student.password_hash):
            raise CredentialException()

        return student

    async def validate_student(self, expected_token_type: str, token: str | bytes) -> Student:

        try:
            payload = decode_jwt(token=token)
            token_type = payload.get(TOKEN_TYPE_FIELD)
            if token_type != expected_token_type:
                raise TokenTypeException(token_type, expected_token_type)

            student_id = uuid.UUID(payload.get("sub"))
            if student_id is None:
                raise CredentialException()
            token_data = TokenData(uid=student_id)

        except jwt.DecodeError:
            raise CredentialException()
        except jwt.ExpiredSignatureError:
            raise CredentialException()

        student = await self.repository.get_student_by_id(token_data.uid)
        if student is None:
            raise CredentialException()

        return student

    async def create_student(self, student: StudentCreate) -> Student:
        if await self.repository.get_student_by_login(student.login) is not None:
            raise LoginExistsException()

        return await self.repository.create_student(student)

    async def get_current_student_for_refresh(self,
                                              token: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Student:
        return await self.validate_student(expected_token_type=REFRESH_TOKEN_TYPE, token=token.credentials)

    async def get_current_student(self, token: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Student:
        return await self.validate_student(expected_token_type=ACCESS_TOKEN_TYPE, token=token.credentials)

    async def get_student_by_id(self, student_id: uuid.UUID) -> Student:
        student = await self.repository.get_student_by_id(student_id)
        if student is None:
            raise NotFoundException()
        return student
