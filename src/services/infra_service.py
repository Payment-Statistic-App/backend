import uuid

from typing import List

from src.models import Group, Semester, OperationTypes
from src.exceptions import AlreadyExistException, NotFoundException
from src.repositories import (
    infra_repository as infra_repo,
    operations_repository as operations_repo,
    user_repository as users_repo
)

from config_data import constants


class InfraService:
    infra_repository = infra_repo.InfraRepository()
    operations_repository = operations_repo.OperationsRepository()
    users_repository = users_repo.UserRepository()

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

    async def create_group(self, group_name: str, initiator_id: uuid.UUID) -> Group:
        if await self.infra_repository.get_group_by_name(group_name):
            raise AlreadyExistException(constants.ALREADY_EXIST_GROUP_MESSAGE)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.group,
            user_id=initiator_id,
            comment=constants.CREATE_GROUP_COMMENT.format(group_name=group_name)
        )

        return await self.infra_repository.create_group(group_name)

    async def create_semester(self, semester_name: str, initiator_id: uuid.UUID) -> Semester:
        if await self.infra_repository.get_semester_by_name(semester_name):
            raise AlreadyExistException(constants.ALREADY_EXIST_SEMESTER_MESSAGE)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.semester,
            user_id=initiator_id,
            comment=constants.CREATE_SEMESTER_COMMENT.format(semester_name=semester_name)
        )

        return await self.infra_repository.create_semester(semester_name)

    async def edit_group(self, group_id: uuid.UUID, new_group_name: str, initiator_id: uuid.UUID) -> Group:
        group = await self.get_group_by_id(group_id)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.group,
            user_id=initiator_id,
            comment=constants.EDIT_GROUP_COMMENT.format(
                name_before=group.name, name_after=new_group_name
            )
        )
        return await self.infra_repository.edit_group(group.id, new_group_name)

    async def edit_semester(self, semester_id: uuid.UUID, new_semester_name: str, initiator_id: uuid.UUID) -> Semester:
        semester = await self.get_semester_by_id(semester_id)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.semester,
            user_id=initiator_id,
            comment=constants.EDIT_SEMESTER_COMMENT.format(
                name_before=semester.name, name_after=new_semester_name
            )
        )

        return await self.infra_repository.edit_semester(semester.id, new_semester_name)

    async def delete_group(self, group_id: uuid.UUID, initiator_id: uuid.UUID) -> None:
        group = await self.get_group_by_id(group_id)
        await self.users_repository.delete_group_for_users_by_id(group.id)

        await self.operations_repository.create_operation(
            operation_type=OperationTypes.group,
            user_id=initiator_id,
            comment=constants.DELETE_GROUP_COMMENT.format(group_name=group.name)
        )

        return await self.infra_repository.delete_group(group.id)

    async def delete_semester(self, semester_id: uuid.UUID, initiator_id: uuid.UUID) -> None:
        semester = await self.get_semester_by_id(semester_id)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.semester,
            user_id=initiator_id,
            comment=constants.DELETE_SEMESTER_COMMENT.format(semester_name=semester.name)
        )
        return await self.infra_repository.delete_semester(semester.id)
