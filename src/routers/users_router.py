import uuid

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query

from src.models import User, Roles
from src.schemas import UserResponse, UserCreate, Token, UserEdit, SuccessfulResponse
from src.services.user_service import UserService

from utils import auth_settings

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/self", response_model=UserResponse)
async def login_for_access_token(
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> UserResponse:
    return UserResponse(**current_user.to_dict())


@router.get("/students", response_model=List[UserResponse])
async def get_students(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        student_id: Optional[uuid.UUID] = Query(None, description="student id for get only one student"),
) -> List[UserResponse]:
    UserService().validate_role(current_user.role, (Roles.admin, Roles.observer, Roles.accountant))

    if student_id is None:
        students = await UserService().get_all_students()
    else:
        students = [await UserService().get_student_by_id(student_id)]

    return list(map(lambda x: UserResponse(**x.to_dict()), students))


@router.post("/new", response_model=UserResponse)
async def create_new_user(
        user_create: UserCreate,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> UserResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    user = await UserService().create_user(user_create, current_user.id)
    return UserResponse(**user.to_dict())


@router.post("/login", response_model=Token)
async def authenticate_user_jwt(user: User = Depends(UserService().authenticate_user)) -> Token:
    access_token = auth_settings.create_access_token(user)
    refresh_token = auth_settings.create_refresh_token(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def refresh_jwt(
        current_user: Annotated[User, Depends(UserService().get_current_user_for_refresh)]
) -> Token:
    access_token = auth_settings.create_access_token(current_user)
    return Token(access_token=access_token)


@router.put("/edit/{user_id}", response_model=UserResponse)
async def edit_user(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        user_id: uuid.UUID,
        new_user_data: UserEdit
) -> UserResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    user = await UserService().edit_user(user_id, new_user_data)
    return UserResponse(**user.to_dict())


@router.delete("/delete/{user_id}", response_model=SuccessfulResponse)
async def delete_user(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        user_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    await UserService().delete_user(user_id)
    return SuccessfulResponse(success="User has been successful delete!")
