import uuid

from typing import Optional, List
from sqlalchemy import insert, select, delete, update

from utils import auth_settings
from src.database import async_session

from src.models import User, Roles
from src.schemas import UserCreate, UserEdit


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

    async def get_all_students(self) -> List[User]:
        async with async_session() as session:
            query = select(User).where(User.role == Roles.student)
            result = await session.execute(query)
            students = result.scalars().all()

        return students

    async def delete_group_for_users_by_id(self, group_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = update(User).where(User.group_id == group_id).values(group_id=None)
            await session.execute(stmt)
            await session.commit()

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

    async def delete_user(self, user_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()
