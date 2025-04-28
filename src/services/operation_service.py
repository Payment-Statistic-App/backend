import uuid
from typing import List

from config_data import constants
from src.exceptions import NotFoundException
from src.models import User, Group, Transaction, Operation, OperationTypes
from src.repositories import operations_repository as operations_repo
from src.schemas import TransactionCreate
from src.services.infra_service import InfraService
from src.services.user_service import UserService


class OperationService:
    operations_repository = operations_repo.OperationsRepository()

    async def get_all_operations(self) -> List[Operation]:
        return await self.operations_repository.get_all_operations()

    async def create_transaction(
            self, user: User, new_transaction: TransactionCreate, initiator_id: uuid.UUID
    ) -> Transaction:
        semester = await InfraService().get_semester_by_id(new_transaction.semester_id)
        await self.operations_repository.create_operation(
            operation_type=OperationTypes.payment,
            user_id=initiator_id,
            comment=constants.PAYMENT_COMMENT.format(
                name=user.name, surname=user.surname, patronymic=user.patronymic, amount=new_transaction.amount
            )
        )
        return await self.operations_repository.create_transaction(user.id, new_transaction, semester.name)

    async def add_student_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID, initiator_id: uuid.UUID) -> Group:
        group = await InfraService().get_group_by_id(group_id)
        student = await UserService().get_student_by_id(user_id)

        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.ADD_TO_GROUP_COMMENT.format(
                name=student.name, surname=student.surname, patronymic=student.patronymic, group_name=group.name
            )
        )

        return await self.operations_repository.add_user_to_group(student.id, group.id)

    async def remove_student_from_group(self, user_id: uuid.UUID, initiator_id: uuid.UUID) -> None:
        student = await UserService().get_student_by_id(user_id)
        if student.group_id is None:
            raise NotFoundException(constants.GROUP_NOT_FOUND_MESSAGE)

        await self.operations_repository.create_operation(
            operation_type=OperationTypes.user,
            user_id=initiator_id,
            comment=constants.REMOVE_FROM_GROUP_COMMENT.format(
                name=student.name, surname=student.surname, patronymic=student.patronymic
            )
        )

        return await self.operations_repository.remove_user_from_group(student.id)
