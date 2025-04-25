from typing import Annotated
from fastapi import APIRouter, Depends

from src.users.models import User, Roles
from src.users.schemas import UserCreate, Token, UserResponse
from src.users.services import UserService

router = APIRouter(tags=["student"], prefix="/student")


@router.get("/self", response_model=UserResponse)
async def login_for_access_token(
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> UserResponse:
    UserService().validate_role(current_user.role, Roles.student)
    return UserResponse(**current_user.to_dict())
