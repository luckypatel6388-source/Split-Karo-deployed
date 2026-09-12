from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense_update import (
    UpdateExpenseRequest,
)
from app.services.expense_management_service import (
    delete_expense,
    get_expense_with_details,
    update_expense_basic,
)
from app.services.group_service import (
    get_user_group,
)
from app.utils.expense_validator import (
    validate_expense_amount,
    validate_expense_title,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expense Management"],
)


@router.patch(
    "/{expense_id}",
)
async def update_expense(
    expense_id: str,
    payload: UpdateExpenseRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    expense = await get_expense_with_details(
        db=db,
        expense_id=expense_id,
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found.",
        )

    group = await get_user_group(
        db=db,
        group_id=expense.group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group.",
        )

    try:

        if payload.title is not None:
            validate_expense_title(
                payload.title
            )

        if payload.amount is not None:
            validate_expense_amount(
                payload.amount
            )

        expense = await update_expense_basic(
            db=db,
            expense=expense,
            title=payload.title,
            description=payload.description,
            amount=payload.amount,
            updated_by=current_user.id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "message": "Expense updated successfully.",
        "expense_id": expense.id,
    }


@router.delete(
    "/{expense_id}",
)
async def remove_expense(
    expense_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    expense = await get_expense_with_details(
        db=db,
        expense_id=expense_id,
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found.",
        )

    group = await get_user_group(
        db=db,
        group_id=expense.group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group.",
        )

    await delete_expense(
        db=db,
        expense=expense,
    )

    return {
        "message": "Expense deleted successfully.",
        "expense_id": expense_id,
    }