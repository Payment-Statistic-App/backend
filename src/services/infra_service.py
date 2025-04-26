import uuid

from typing import List

from src.models import Group, Semester
from src.exceptions import AlreadyExistException, NotFoundException
from src.repositories import (
    user_repository as user_repo,
    infra_repository as infra_repo,
    operations_repository as operations_repo
)

from config_data import constants


class InfraService:
    user_repository = user_repo.UserRepository()
    infra_repository = infra_repo.InfraRepository()
    operations_repository = operations_repo.OperationsRepository()

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

    async def get_all_groups(self) -> List[Group]:
        return await self.infra_repository.get_all_groups()

    async def get_all_semesters(self) -> List[Semester]:
        return await self.infra_repository.get_all_semesters()

    async def create_group(self, group_name: str) -> Group:
        if await self.infra_repository.get_group_by_name(group_name):
            raise AlreadyExistException(constants.ALREADY_EXIST_GROUP_MESSAGE)
        return await self.infra_repository.create_group(group_name)

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

    async def delete_group(self, group_id: uuid.UUID) -> None:
        group = await self.get_group_by_id(group_id)
        return await self.infra_repository.delete_group(group.id)

    async def delete_semester(self, semester_id: uuid.UUID) -> None:
        semester = await self.get_semester_by_id(semester_id)
        return await self.infra_repository.delete_semester(semester.id)
