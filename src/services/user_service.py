import uuid
import jwt

from typing import Optional, List, Tuple
from fastapi import Depends, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.models import User, Roles, OperationTypes
from src.schemas import UserCreate, TokenData, UserLogin, UserEdit
from src.exceptions import CredentialException, TokenTypeException, AlreadyExistException, NotFoundException, \
    AccessException, IncorrectFileFormatException, ErrorLoadFileException
from src.repositories import (
    user_repository as user_repo,
    infra_repository as infra_repo,
    operations_repository as operations_repo
)

from config_data import constants
from utils import auth_settings
from utils.excel_parser import Parser as XlsxParser

http_bearer = HTTPBearer()


class UserService:
    user_repository = user_repo.UserRepository()
    infra_repository = infra_repo.InfraRepository()
    operations_repository = operations_repo.OperationsRepository()

    @staticmethod
    def validate_role(current_role: Roles, expected_roles: Tuple[Roles, ...]) -> bool:
        if current_role not in expected_roles:
            raise AccessException()
        return True

    async def authenticate_user(self, user_data: UserLogin) -> Optional[User]:
        user = await self.user_repository.get_user_by_login(user_data.login)
        if not user:
            raise CredentialException()
        if not auth_settings.validate_password(user_data.password, user.password_hash):
            raise CredentialException()

        return user

    async def validate_user(self, expected_token_type: str, token: str | bytes) -> User:

        try:
            payload = auth_settings.decode_jwt(token=token)
            token_type = payload.get(constants.TOKEN_TYPE_FIELD)
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

        user = await self.user_repository.get_user_by_id(token_data.uid)
        if user is None:
            raise CredentialException()

        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_student_by_id(self, student_id: uuid.UUID) -> User:
        student = await self.user_repository.get_user_by_id(student_id)
        if student is None or student.role != Roles.student:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        return student

    async def get_all_students(self) -> List[User]:
        return await self.user_repository.get_all_students()

    async def get_all_users(self) -> List[User]:
        return await self.user_repository.get_all_users()

    async def get_current_user_for_refresh(
            self,
            token: HTTPAuthorizationCredentials = Depends(http_bearer)
    ) -> User:
        return await self.validate_user(expected_token_type=constants.REFRESH_TOKEN_TYPE, token=token.credentials)

    async def get_current_user(
            self,
            token: HTTPAuthorizationCredentials = Depends(http_bearer)
    ) -> User:
        return await self.validate_user(expected_token_type=constants.ACCESS_TOKEN_TYPE, token=token.credentials)

    async def create_user(self, user: UserCreate, initiator_id: uuid.UUID) -> User:
        if await self.user_repository.get_user_by_login(user.login) is not None:
            raise AlreadyExistException(constants.ALREADY_EXIST_USER_MESSAGE)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.CREATE_USER_COMMENT.format(
                name=user.name, surname=user.surname, patronymic=user.patronymic, role=user.role.value
            )
        )

        return await self.user_repository.create_user(user)

    async def load_users_from_file(self, xlsx_file: UploadFile, initiator_id: uuid.UUID) -> List[User]:
        if not xlsx_file.filename.endswith('.xlsx'):
            raise IncorrectFileFormatException()

        try:
            xlsx_parser = XlsxParser(xlsx_file)
            users = xlsx_parser.parse_users()
        except Exception:
            await xlsx_file.close()
            raise ErrorLoadFileException()

        users_create_response: List[User] = []
        for user in users:
            try:
                new_user = await self.user_repository.create_user(UserCreate(**user))
                users_create_response.append(new_user)
            except Exception:
                continue

        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.LOAD_USERS_COMMENT.format(count=len(users_create_response))
        )

        await xlsx_file.close()

        return users_create_response

    async def edit_user(self, user_id: uuid.UUID, new_user_data: UserEdit, initiator_id: uuid.UUID) -> User:
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.EDIT_USER_COMMENT.format(
                name=user.name, surname=user.surname, patronymic=user.patronymic
            )
        )
        return await self.user_repository.edit_user(user.id, new_user_data)

    async def delete_user(self, user_id: uuid.UUID, initiator_id: uuid.UUID) -> None:
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        if user.role == Roles.admin:
            raise AccessException()

        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.DELETE_USER_COMMENT.format(
                name=user.name, surname=user.surname, patronymic=user.patronymic, role=user.role.value
            )
        )
        return await self.user_repository.delete_user(user_id)
