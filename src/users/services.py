import uuid
import jwt

from typing import Optional, List
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.models import User, Roles, Group, Semester, Transaction
from src.schemas import UserCreate, TokenData, UserLogin, UserEdit, TransactionCreate
from src.exceptions import CredentialException, TokenTypeException, AlreadyExistException, NotFoundException
from src.repositories import (
    user_repository as user_repo,
    infra_repository as infra_repo,
    operations_repository as operations_repo
)

from config_data import constants
from utils import auth_settings

http_bearer = HTTPBearer()


class UserService:
    user_repository = user_repo.UserRepository()
    infra_repository = infra_repo.InfraRepository()
    operations_repository = operations_repo.OperationsRepository()

    async def authenticate_user(self, user_data: UserLogin) -> Optional[User]:
        user = await self.user_repository.get_user_by_login(user_data.login)
        if not user:
            raise CredentialException()
        if not auth_settings.validate_password(user_data.password, user.password_hash):
            raise CredentialException()
        self.validate_role(user.role, user_data.role)

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

    async def create_user(self, user: UserCreate) -> User:
        if await self.user_repository.get_user_by_login(user.login) is not None:
            raise AlreadyExistException(constants.ALREADY_EXIST_USER_MESSAGE)

        return await self.user_repository.create_user(user)

    async def get_current_user_for_refresh(
            self,
            token: HTTPAuthorizationCredentials = Depends(http_bearer)
    ) -> User:
        return await self.validate_user(expected_token_type=constants.REFRESH_TOKEN_TYPE, token=token.credentials)

    @staticmethod
    def validate_role(current_role: Roles, expected_role: Roles) -> bool:
        if current_role != expected_role:
            raise CredentialException()
        return True

    async def get_current_user(
            self,
            token: HTTPAuthorizationCredentials = Depends(http_bearer)
    ) -> User:
        return await self.validate_user(expected_token_type=constants.ACCESS_TOKEN_TYPE, token=token.credentials)

    async def get_group_by_id(self, group_id: uuid.UUID) -> Group:
        group = await self.infra_repository.get_group_by_id(group_id)
        if group is None:
            raise NotFoundException(constants.GROUP_NOT_FOUND_MESSAGE)

        return group

    async def get_semester_by_id(self, semester_id: uuid.UUID) -> Semester:
        semester = await self.infra_repository.get_semester_by_id(semester_id)
        if semester is None:
            raise NotFoundException(constants.SEMESTER_NOT_FOUND_MESSAGE)

        return semester

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_student_by_id(self, student_id: uuid.UUID) -> User:
        student = await self.user_repository.get_user_by_id(student_id)
        if student is None or student.role != Roles.student:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        return student

    async def get_all_students(self) -> List[User]:
        return await self.user_repository.get_all_students()

    async def get_all_groups(self) -> List[Group]:
        return await self.infra_repository.get_all_groups()

    async def get_all_semesters(self) -> List[Semester]:
        return await self.infra_repository.get_all_semesters()

    async def create_group(self, group_name: str) -> Group:
        if await self.infra_repository.get_group_by_name(group_name):
            raise AlreadyExistException(constants.ALREADY_EXIST_GROUP_MESSAGE)
        return await self.infra_repository.create_group(group_name)

    async def create_transaction(self, user: User, new_transaction: TransactionCreate) -> Transaction:
        semester = await self.get_semester_by_id(new_transaction.semester_id)
        return await self.operations_repository.create_transaction(user.id, new_transaction, semester.name)

    async def create_semester(self, semester_name: str) -> Semester:
        if await self.infra_repository.get_semester_by_name(semester_name):
            raise AlreadyExistException(constants.ALREADY_EXIST_SEMESTER_MESSAGE)
        return await self.infra_repository.create_semester(semester_name)

    async def edit_group(self, group_id: uuid.UUID, new_group_name: str) -> Group:
        group = await self.get_group_by_id(group_id)
        return await self.infra_repository.edit_group(group.id, new_group_name)

    async def edit_semester(self, semester_id: uuid.UUID, new_semester_name: str) -> Semester:
        semester = await self.get_semester_by_id(semester_id)
        return await self.infra_repository.edit_semester(semester.id, new_semester_name)

    async def edit_user(self, user_id: uuid.UUID, new_user_data: UserEdit) -> User:
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        return await self.user_repository.edit_user(user.id, new_user_data)

    async def delete_group(self, group_id: uuid.UUID) -> None:
        group = await self.get_group_by_id(group_id)
        return await self.infra_repository.delete_group(group.id)

    async def delete_semester(self, semester_id: uuid.UUID) -> None:
        semester = await self.get_semester_by_id(semester_id)
        return await self.infra_repository.delete_semester(semester.id)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(constants.USER_NOT_FOUND_MESSAGE)
        return await self.user_repository.delete_user(user_id)

    async def add_student_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Group:
        group = await self.get_group_by_id(group_id)
        student = await self.get_student_by_id(user_id)

        return await self.operations_repository.add_user_to_group(student.id, group.id)
