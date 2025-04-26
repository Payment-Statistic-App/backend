import uuid

from typing import Optional, List
from sqlalchemy import insert, select, delete, update

from utils import auth_settings
from src.database import async_session
from config_data import constants

from src.users.models import User, Group, Roles, Semester, Transaction
from src.users.schemas import UserCreate, UserEdit, TransactionCreate


class UserRepository:

    async def get_user_by_login(self, login: str) -> Optional[User]:
        async with async_session() as session:
            query = select(User).where(User.login == login)
            result = await session.execute(query)
            user = result.scalars().first()
        return user

    async def get_all_users(self) -> List[User]:
        async with async_session() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars().all()

            return users

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        async with async_session() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

        return user

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Transaction:
        async with async_session() as session:
            query = select(Transaction).where(Transaction.id == transaction_id)
            result = await session.execute(query)
            transaction = result.scalars().first()

        return transaction

    async def get_group_by_name(self, group_name: str) -> Group:
        async with async_session() as session:
            query = select(Group).where(Group.name == group_name)
            result = await session.execute(query)
            group = result.scalars().first()

        return group

    async def get_group_by_id(self, group_id: uuid.UUID) -> Group:
        async with async_session() as session:
            query = select(Group).where(Group.id == group_id)
            result = await session.execute(query)
            group = result.scalars().first()

        return group

    async def get_semester_by_name(self, semester_name: str) -> Semester:
        async with async_session() as session:
            query = select(Semester).where(Semester.name == semester_name)
            result = await session.execute(query)
            semester = result.scalars().first()

        return semester

    async def get_semester_by_id(self, semester_id: uuid.UUID) -> Semester:
        async with async_session() as session:
            query = select(Semester).where(Semester.id == semester_id)
            result = await session.execute(query)
            semester = result.scalars().first()

        return semester

    async def create_user(self, new_user: UserCreate) -> User:
        password = new_user.password
        user_dc = new_user.dict(exclude={"password"})
        user_dc["password_hash"] = auth_settings.hash_password(password)
        user_dc["id"] = uuid.uuid4()

        async with async_session() as session:
            stmt = insert(User).values(**user_dc)
            await session.execute(stmt)
            await session.commit()

        return await self.get_user_by_id(user_dc["id"])

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

    async def create_group(self, group_name: str) -> Group:
        async with async_session() as session:
            stmt = insert(Group).values(name=group_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_group_by_name(group_name)

    async def create_semester(self, semester_name: str) -> Semester:
        async with async_session() as session:
            stmt = insert(Semester).values(name=semester_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_semester_by_name(semester_name)

    async def edit_group(self, group_id: uuid.UUID, new_group_name: str) -> Group:
        async with async_session() as session:
            stmt = update(Group).where(Group.id == group_id).values(name=new_group_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_group_by_id(group_id)

    async def edit_semester(self, semester_id: uuid.UUID, new_semester_name: str) -> Semester:
        async with async_session() as session:
            stmt = update(Semester).where(Semester.id == semester_id).values(name=new_semester_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_semester_by_id(semester_id)

    async def edit_user(self, user_id: uuid.UUID, new_user_data: UserEdit) -> User:
        async with async_session() as session:
            stmt = update(User).where(User.id == user_id).values(
                name=new_user_data.name,
                surname=new_user_data.surname,
                patronymic=new_user_data.patronymic,
                phone=new_user_data.phone,
            )
            await session.execute(stmt)
            await session.commit()

        return await self.get_user_by_id(user_id)

    async def delete_group(self, group_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(Group).where(Group.id == group_id)
            await session.execute(stmt)
            await session.commit()

    async def delete_user(self, user_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def delete_semester(self, semester_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(Semester).where(Semester.id == semester_id)
            await session.execute(stmt)
            await session.commit()

    async def add_user_to_group(self, user_id: uuid.UUID, group_id: uuid.UUID) -> Group:
        async with async_session() as session:
            stmt = update(User).where(User.id == user_id).values(group_id=group_id)
            await session.execute(stmt)
            await session.commit()

        return await self.get_group_by_id(group_id)

    async def get_all_students(self) -> List[User]:
        async with async_session() as session:
            query = select(User).where(User.role == Roles.student)
            result = await session.execute(query)
            students = result.scalars().all()

        return students

    async def get_all_groups(self) -> List[Group]:
        async with async_session() as session:
            query = select(Group)
            result = await session.execute(query)
            groups = result.scalars().all()

        return groups

    async def get_all_semesters(self) -> List[Semester]:
        async with async_session() as session:
            query = select(Semester)
            result = await session.execute(query)
            semesters = result.scalars().all()

        return semesters
