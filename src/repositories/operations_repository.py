import uuid

from sqlalchemy import insert, select, update

from src.database import async_session
from config_data import constants

from src.models import User, Group, Transaction
from src.schemas import TransactionCreate
from src.repositories.infra_repository import InfraRepository


class OperationsRepository:
    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Transaction:
        async with async_session() as session:
            query = select(Transaction).where(Transaction.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalars().first()

        return transaction

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

    async def add_user_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Group:
        async with async_session() as session:
            stmt = update(User).where(User.id == user_id).values(group_id=group_id)
            await session.execute(stmt)
            await session.commit()

        return await InfraRepository().get_group_by_id(group_id)
