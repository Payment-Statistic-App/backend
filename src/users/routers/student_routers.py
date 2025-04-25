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


@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def refresh_jwt(
        current_user: Annotated[User, Depends(UserService().get_current_user_for_refresh)]
) -> Token:
    UserService().validate_role(current_user.role, Roles.student)
    access_token = UserService().create_access_token(current_user)
    return Token(access_token=access_token)
