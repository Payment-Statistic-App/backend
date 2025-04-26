from typing import Annotated
from fastapi import APIRouter, Depends

from src.models import User, Roles
from src.schemas import UserResponse, TransactionResponse, TransactionCreate
from src.services.user_service import UserService
from src.services.operation_service import OperationService

router = APIRouter(tags=["student"], prefix="/student")


@router.get("/self", response_model=UserResponse)
async def login_for_access_token(
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> UserResponse:
    UserService().validate_role(current_user.role, (Roles.student,))

    return UserResponse(**current_user.to_dict())


@router.post("/new_transaction", response_model=TransactionResponse)
async def new_semester_payment(
        new_transaction: TransactionCreate,
        current_user: Annotated[User, Depends(UserService().get_current_user)]
) -> TransactionResponse:
    UserService().validate_role(current_user.role, (Roles.student,))

    transaction = await OperationService().create_transaction(current_user, new_transaction)
    return TransactionResponse(**transaction.to_dict())
