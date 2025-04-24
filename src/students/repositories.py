import uuid

from typing import Optional, List
from sqlalchemy import insert, select, delete

from utils import auth_settings
from src.database import async_session

from src.students.models import Student
from src.students.schemas import StudentCreate


class StudentRepository:
    async def create_student(self, new_student: StudentCreate) -> Student:
        password = new_student.password
        student_dc = new_student.dict(exclude={"password"})
        student_dc["password_hash"] = auth_settings.hash_password(password)
        student_dc["id"] = uuid.uuid4()

        async with async_session() as session:
            stmt = insert(Student).values(**student_dc)
            await session.execute(stmt)
            await session.commit()

            query = select(Student).where(Student.id == student_dc["id"])
            result = await session.execute(query)
            student = result.scalars().first()

        return student

    async def get_student_by_login(self, login: str) -> Optional[Student]:
        async with async_session() as session:
            query = select(Student).where(Student.login == login)
            result = await session.execute(query)
            student = result.scalars().first()
        return student

    async def get_all_students(self) -> List[Student]:
        async with async_session() as session:
            query = select(Student)
            result = await session.execute(query)
            students = result.scalars().all()

            return students

    async def get_student_by_id(self, student_id: uuid.UUID) -> Optional[Student]:
        async with async_session() as session:
            query = select(Student).where(Student.id == student_id)
            result = await session.execute(query)
            student = result.scalars().first()

        return student

    async def delete_student_by_id(self, student_id: uuid.UUID) -> None:
        async with async_session() as session:
            stmt = delete(Student).where(Student.id == student_id)
            await session.execute(stmt)
            await session.commit()
