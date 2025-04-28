import uuid

from config_data import constants
from src.exceptions import NotFoundException
from src.models import User, Group, Transaction
from src.repositories import (
    user_repository as user_repo,
    infra_repository as infra_repo,
    operations_repository as operations_repo
)
from src.schemas import TransactionCreate
from src.services.infra_service import InfraService
from src.services.user_service import UserService


class OperationService:
    user_repository = user_repo.UserRepository()
    infra_repository = infra_repo.InfraRepository()
    operations_repository = operations_repo.OperationsRepository()

    async def create_transaction(self, user: User, new_transaction: TransactionCreate) -> Transaction:
        semester = await InfraService().get_semester_by_id(new_transaction.semester_id)
        return await self.operations_repository.create_transaction(user.id, new_transaction, semester.name)

    async def add_student_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Group:
        group = await InfraService().get_group_by_id(group_id)
        student = await UserService().get_student_by_id(user_id)

        return await self.operations_repository.add_user_to_group(student.id, group.id)

    async def remove_student_from_group(self, user_id: uuid.UUID) -> None:
        student = await UserService().get_student_by_id(user_id)
        if student.group_id is None:
            raise NotFoundException(constants.GROUP_NOT_FOUND_MESSAGE)

        return await self.operations_repository.remove_user_from_group(student.id)
