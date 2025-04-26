import uuid

from typing import List
from sqlalchemy import insert, select, delete, update

from src.database import async_session
from src.models import Group, Semester


class InfraRepository:
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

    async def get_semester_by_id(self, semester_id: uuid.UUID) -> Semester:
        async with async_session() as session:
            query = select(Semester).where(Semester.id == semester_id)
            result = await session.execute(query)
            semester = result.scalars().first()

        return semester

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

    async def delete_group(self, group_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(Group).where(Group.id == group_id)
            await session.execute(stmt)
            await session.commit()

    async def delete_semester(self, semester_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(Semester).where(Semester.id == semester_id)
            await session.execute(stmt)
            await session.commit()
