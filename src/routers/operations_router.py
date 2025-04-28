import uuid

from typing import Annotated, List
from fastapi import APIRouter, Depends

from src.models import User, Roles
from src.schemas import GroupResponse, TransactionResponse, TransactionCreate, SuccessfulResponse, OperationResponse
from src.services.user_service import UserService
from src.services.operation_service import OperationService

router = APIRouter(tags=["operations"], prefix="/operations")


@router.get("/show_list", response_model=List[OperationResponse])
async def get_operations_list(
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> List[OperationResponse]:
    UserService().validate_role(current_user.role, (Roles.admin,))

    operations = await OperationService().get_all_operations()
    return list(map(lambda x: OperationResponse(**x.to_dict()), operations))


@router.post("/new_transaction", response_model=TransactionResponse)
async def new_semester_payment(
        new_transaction: TransactionCreate,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> TransactionResponse:
    UserService().validate_role(current_user.role, (Roles.student,))

    transaction = await OperationService().create_transaction(current_user, new_transaction)
    return TransactionResponse(**transaction.to_dict())


@router.put("/add_to_group", response_model=GroupResponse)
async def add_student_to_group(
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> GroupResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    group = await OperationService().add_student_to_group(user_id, group_id)
    return GroupResponse(**group.to_dict())


@router.delete("/remove_from_group", response_model=SuccessfulResponse)
async def remove_student_from_group(
        user_id: uuid.UUID,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> SuccessfulResponse:
    UserService().validate_role(current_user.role, (Roles.admin,))

    await OperationService().remove_student_from_group(user_id)
    return SuccessfulResponse(success="Student successfully delete from group!")
