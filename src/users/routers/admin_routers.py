import uuid
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, Query

from src.users.models import User, Roles
from src.users.schemas import UserCreate, GroupResponse, UserResponse, SuccessfulResponse, UserEdit, SemesterResponse
from src.users.services import UserService

router = APIRouter(tags=["admin"], prefix="/admin")


@router.get("/students", response_model=List[UserResponse])
async def get_students(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        student_id: Optional[uuid.UUID] = Query(None, description="student id for get only one student"),
) -> List[UserResponse]:
    UserService().validate_role(current_user.role, Roles.admin)

    if student_id is None:
        students = await UserService().get_all_students()
    else:
        students = [await UserService().get_student_by_id(student_id)]

    return list(map(lambda x: UserResponse(**x.to_dict()), students))


@router.get("/groups", response_model=List[GroupResponse])
async def get_groups(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: Optional[uuid.UUID] = Query(None, description="group id for get only one group"),
) -> List[GroupResponse]:
    UserService().validate_role(current_user.role, Roles.admin)

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


@router.post("/create_semester", response_model=SemesterResponse)
async def create_new_semester(
        semester_name: str,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> SemesterResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    new_semester = await UserService().create_semester(semester_name)
    return SemesterResponse(**new_semester.to_dict())


@router.put("/edit_group/{group_id}", response_model=GroupResponse)
async def edit_group(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: uuid.UUID,
        new_group_name: str
) -> GroupResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    group = await UserService().edit_group(group_id, new_group_name)
    return GroupResponse(**group.to_dict())


@router.put("/edit_semester/{semester_id}", response_model=SemesterResponse)
async def edit_semester(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        semester_id: uuid.UUID,
        new_semester_name: str
) -> SemesterResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    semester = await UserService().edit_semester(semester_id, new_semester_name)
    return SemesterResponse(**semester.to_dict())


@router.put("/edit_user/{user_id}", response_model=UserResponse)
async def edit_user(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        user_id: uuid.UUID,
        new_user_data: UserEdit
) -> UserResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    user = await UserService().edit_user(user_id, new_user_data)
    return UserResponse(**user.to_dict())


@router.put("/add_to_group", response_model=GroupResponse)
async def add_student_to_group(
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> GroupResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    group = await UserService().add_student_to_group(user_id, group_id)
    return GroupResponse(**group.to_dict())


@router.delete("/delete_group/{group_id}", response_model=SuccessfulResponse)
async def delete_group(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    await UserService().delete_group(group_id)
    return SuccessfulResponse(success="Group has been successful delete!")


@router.delete("/delete_semester/{semester_id}", response_model=SuccessfulResponse)
async def delete_semester(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        semester_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    await UserService().delete_semester(semester_id)
    return SuccessfulResponse(success="Semester has been successful delete!")


@router.delete("/delete_user/{user_id}", response_model=SuccessfulResponse)
async def delete_user(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        user_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, Roles.admin)

    await UserService().delete_user(user_id)
    return SuccessfulResponse(success="User has been successful delete!")
