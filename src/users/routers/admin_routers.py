import uuid
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, Query

from src.users.models import User, Roles
from src.users.schemas import UserCreate, GroupResponse, UserResponse
from src.users.services import UserService

router = APIRouter(tags=["admin"], prefix="/admin")


@router.get("/students", response_model=List[UserResponse])
async def get_students(
        student_id: Optional[uuid.UUID] = Query(None, description="student id for get only one student"),
) -> List[UserResponse]:
    if student_id is None:
        students = await UserService().get_all_students()
    else:
        students = [await UserService().get_student_by_id(student_id)]

    return list(map(lambda x: UserResponse(**x.to_dict()), students))


@router.get("/groups", response_model=List[GroupResponse])
async def get_students(
        group_id: Optional[uuid.UUID] = Query(None, description="group id for get only one group"),
) -> List[GroupResponse]:
    if group_id is None:
        groups = await UserService().get_all_groups()
    else:
        groups = [await UserService().get_group_by_id(group_id)]

    return list(map(lambda x: GroupResponse(**x.to_dict()), groups))


@router.post("/create_user", response_model=UserResponse)
async def create_new_user(
        user_create: UserCreate,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> UserResponse:
    UserService().validate_role(current_user.role, Roles.admin)
    user = await UserService().create_user(user_create)
    return UserResponse(**user.to_dict())


@router.post("/create_group", response_model=GroupResponse)
async def create_new_group(
        group_name: str,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> GroupResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    new_group = await UserService().create_group(group_name)
    return GroupResponse(**new_group.to_dict())


@router.put("/add_to_group", response_model=GroupResponse)
async def add_student_to_group(
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> GroupResponse:
    UserService().validate_role(current_user.role, Roles.admin)
    group = await UserService().add_student_to_group(user_id, group_id)
    return GroupResponse(**group.to_dict())
