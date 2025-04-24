import uuid
import jwt

from datetime import timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config_data.config import Config, load_config
from utils.auth_settings import validate_password, decode_jwt, encode_jwt

from src.users.models import User
from src.users.repositories import UserRepository
from src.users.schemas import UserCreate, TokenData, UserLogin
from src.users.exceptions import CredentialException, TokenTypeException, NotFoundException, LoginExistsException

http_bearer = HTTPBearer()

settings: Config = load_config(".env")
auth_config = settings.authJWT

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class UserService:
    repository = UserRepository()

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

    def create_access_token(self, user: User) -> str:
        jwt_payload = {
            "sub": str(user.id),
            "login": user.login,
        }
        return self.create_jwt(
            token_type=ACCESS_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_minutes=auth_config.access_token_expire_minutes
        )

    def create_refresh_token(self, user: User) -> str:
        jwt_payload = {
            "sub": str(user.id),
            "login": user.login,
        }
        return self.create_jwt(
            token_type=REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=auth_config.refresh_token_expire_days)
        )

    async def authenticate_user(self, user_data: UserLogin) -> Optional[User]:
        user = await self.repository.get_user_by_login(user_data.login)
        if not user:
            raise CredentialException()
        if not validate_password(user_data.password, user.password_hash):
            raise CredentialException()

        return user

    async def validate_user(self, expected_token_type: str, token: str | bytes) -> User:

        try:
            payload = decode_jwt(token=token)
            token_type = payload.get(TOKEN_TYPE_FIELD)
            if token_type != expected_token_type:
                raise TokenTypeException(token_type, expected_token_type)

            user_id = uuid.UUID(payload.get("sub"))
            if user_id is None:
                raise CredentialException()
            token_data = TokenData(uid=user_id)

        except jwt.DecodeError:
            raise CredentialException()
        except jwt.ExpiredSignatureError:
            raise CredentialException()

        user = await self.repository.get_user_by_id(token_data.uid)
        if user is None:
            raise CredentialException()

        return user

    async def create_user(self, user: UserCreate) -> User:
        if await self.repository.get_user_by_login(user.login) is not None:
            raise LoginExistsException()

        return await self.repository.create_user(user)

    async def get_current_user_for_refresh(self, token: HTTPAuthorizationCredentials = Depends(http_bearer)) -> User:
        return await self.validate_user(expected_token_type=REFRESH_TOKEN_TYPE, token=token.credentials)

    async def get_current_user(self, token: HTTPAuthorizationCredentials = Depends(http_bearer)) -> User:
        return await self.validate_user(expected_token_type=ACCESS_TOKEN_TYPE, token=token.credentials)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException()
        return user
