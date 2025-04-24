import uuid

from typing import Optional, List
from sqlalchemy import insert, select, delete

from utils import auth_settings
from src.database import async_session

from src.users.models import User
from src.users.schemas import UserCreate


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

    async def delete_user_by_id(self, user_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()
