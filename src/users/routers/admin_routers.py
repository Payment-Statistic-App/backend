from typing import Annotated
from fastapi import APIRouter, Depends

from src.users.models import User, Roles
from src.users.schemas import UserCreate, Token
from src.users.services import UserService

router = APIRouter(tags=["admin"], prefix="/admin")


@router.post("/create_student")
async def create_student(
        user_create: UserCreate,
        # current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> Token:
    # UserService().validate_role(current_user.role, Roles.admin)
    student = await UserService().create_user(user_create)

    access_token = UserService().create_access_token(student)
    refresh_token = UserService().create_refresh_token(student)

    return Token(access_token=access_token, refresh_token=refresh_token)
