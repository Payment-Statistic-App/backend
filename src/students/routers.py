from typing import Annotated
from fastapi import APIRouter, Depends

from src.students.models import Student
from src.students.schemas import StudentCreate, Token, StudentResponse
from src.students.services import StudentService

router = APIRouter(tags=["student"], prefix="/student")


@router.post("/register")
async def register(student_create: StudentCreate) -> Token:
    student = await StudentService().create_student(student_create)
    access_token = StudentService().create_access_token(student)
    refresh_token = StudentService().create_refresh_token(student)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
async def authenticate_student_jwt(student: Student = Depends(StudentService().authenticate_student)) -> Token:
    access_token = StudentService().create_access_token(student)
    refresh_token = StudentService().create_refresh_token(student)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def refresh_jwt(
        student: Annotated[Student, Depends(StudentService().get_current_student_for_refresh)]
) -> Token:
    access_token = StudentService().create_access_token(student)
    return Token(access_token=access_token)


@router.get("/self", response_model=StudentResponse)
async def login_for_access_token(
        current_student: Annotated[Student, Depends(StudentService().get_current_student)]
) -> StudentResponse:
    return StudentResponse(**current_student.to_dict())
