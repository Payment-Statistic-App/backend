import uuid

from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, Query

from src.models import User, Roles
from src.schemas import GroupResponse, SuccessfulResponse, SemesterResponse
from src.services.user_service import UserService
from src.services.infra_service import InfraService

router = APIRouter(tags=["infra"], prefix="/infra")


@router.get("/semesters", response_model=List[SemesterResponse])
async def get_semesters_list() -> List[SemesterResponse]:
    semesters = await InfraService().get_all_semesters()
    return list(map(lambda x: SemesterResponse(**x.to_dict()), semesters))


@router.get("/groups", response_model=List[GroupResponse])
async def get_groups(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: Optional[uuid.UUID] = Query(None, description="group id for get only one group"),
) -> List[GroupResponse]:
    UserService().validate_role(current_user.role, (Roles.admin, Roles.accountant))

    if group_id is None:
        groups = await InfraService().get_all_groups()
    else:
        groups = [await InfraService().get_group_by_id(group_id)]

    return list(map(lambda x: GroupResponse(**x.to_dict()), groups))


@router.post("/new_group", response_model=GroupResponse)
async def create_new_group(
        group_name: str,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> GroupResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    new_group = await InfraService().create_group(group_name)
    return GroupResponse(**new_group.to_dict())


@router.post("/new_semester", response_model=SemesterResponse)
async def create_new_semester(
        semester_name: str,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> SemesterResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    new_semester = await InfraService().create_semester(semester_name)
    return SemesterResponse(**new_semester.to_dict())


@router.put("/edit_group/{group_id}", response_model=GroupResponse)
async def edit_group(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: uuid.UUID,
        new_group_name: str
) -> GroupResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    group = await InfraService().edit_group(group_id, new_group_name)
    return GroupResponse(**group.to_dict())


@router.put("/edit_semester/{semester_id}", response_model=SemesterResponse)
async def edit_semester(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        semester_id: uuid.UUID,
        new_semester_name: str
) -> SemesterResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    semester = await InfraService().edit_semester(semester_id, new_semester_name)
    return SemesterResponse(**semester.to_dict())


@router.delete("/delete_group/{group_id}", response_model=SuccessfulResponse)
async def delete_group(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        group_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    await InfraService().delete_group(group_id)
    return SuccessfulResponse(success="Group has been successful delete!")


@router.delete("/delete_semester/{semester_id}", response_model=SuccessfulResponse)
async def delete_semester(
        current_user: Annotated[User, Depends(UserService().get_current_user)],
        semester_id: uuid.UUID,
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    await InfraService().delete_semester(semester_id)
    return SuccessfulResponse(success="Semester has been successful delete!")
