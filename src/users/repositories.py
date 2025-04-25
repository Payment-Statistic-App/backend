import uuid

from typing import Optional, List
from sqlalchemy import insert, select, delete, update

from utils import auth_settings
from src.database import async_session

from src.users.models import User, Group, Roles
from src.users.schemas import UserCreate, UserEdit


class UserRepository:
    async def create_user(self, new_user: UserCreate) -> User:
        password = new_user.password
        user_dc = new_user.dict(exclude={"password"})
        user_dc["password_hash"] = auth_settings.hash_password(password)
        user_dc["id"] = uuid.uuid4()

        async with async_session() as session:
            stmt = insert(User).values(**user_dc)
            await session.execute(stmt)
            await session.commit()

            query = select(User).where(User.id == user_dc["id"])
            result = await session.execute(query)
            user = result.scalars().first()

        return user

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

    async def create_group(self, group_name: str) -> Group:
        async with async_session() as session:
            stmt = insert(Group).values(name=group_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_group_by_name(group_name)

    async def edit_group(self, group_id: uuid.UUID, new_group_name: str) -> Group:
        async with async_session() as session:
            stmt = update(Group).where(Group.id == group_id).values(name=new_group_name)
            await session.execute(stmt)
            await session.commit()

        return await self.get_group_by_id(group_id)

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

    async def delete_user_by_id(self, user_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()
