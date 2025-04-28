import uuid
from typing import List

from sqlalchemy import insert, select, update

from src.database import async_session
from config_data import constants

from src.models import User, Group, Transaction, Operation, OperationTypes
from src.schemas import TransactionCreate
from src.repositories.infra_repository import InfraRepository


class OperationsRepository:
    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Transaction:
        async with async_session() as session:
            query = select(Transaction).where(Transaction.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalars().first()

        return transaction

    async def get_operation_by_id(self, operation_id: uuid.UUID) -> Operation:
        async with async_session() as session:
            query = select(Operation).where(Operation.id == operation_id)
            result = await session.execute(query)
            operation = result.scalars().first()

        return operation

    async def get_all_operations(self) -> List[Operation]:
        async with async_session() as session:
            query = select(Operation)
            result = await session.execute(query)
            operations = result.scalars().all

        return operations


    async def create_transaction(self, user_id: uuid.UUID, new_transaction: TransactionCreate, semester_name: str):
        transaction_dc = new_transaction.dict()
        transaction_dc["id"] = uuid.uuid4()
        transaction_dc["user_id"] = user_id
        transaction_dc["comment"] = constants.TRANSACTION_COMMENT.format(
            semester_name=semester_name, amount=new_transaction.amount
        )

        async with async_session() as session:
            stmt = insert(Transaction).values(**transaction_dc)
            await session.execute(stmt)
            await session.commit()

        return await self.get_transaction_by_id(transaction_dc["id"])

    async def create_operation(self, operation_type: OperationTypes, user_id: uuid.UUID, comment: str) -> Operation:
        operation_id = uuid.uuid4()
        async with async_session() as session:
            stmt = insert(Operation).values(id=operation_id, type=operation_type, user_id=user_id, comment=comment)
            await session.execute(stmt)
            await session.commit()

        return await self.get_operation_by_id(operation_id)

    async def add_user_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Group:
        async with async_session() as session:
            stmt = update(User).where(User.id == user_id).values(group_id=group_id)
            await session.execute(stmt)
            await session.commit()

        return await InfraRepository().get_group_by_id(group_id)

    async def remove_user_from_group(self, user_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = update(User).where(User.id == user_id).values(group_id=None)
            await session.execute(stmt)
            await session.commit()
