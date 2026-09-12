from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.schemas.expense_item import (
    CreateExpenseItemRequest,
    ExpenseItemParticipantResponse,
    ExpenseItemResponse,
)
from app.services.group_service import (
    get_user_group,
)
from app.services.item_expense_service import (
    add_item_to_expense,
)


router = APIRouter(
    prefix="/expenses/{expense_id}/items",
    tags=["Expense Items"],
)


@router.post(
    "",
    response_model=ExpenseItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense_item(
    expense_id: str,
    payload: CreateExpenseItemRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    # Get the expense.
    from sqlalchemy import select
    from app.models.expense import Expense

    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id
        )
    )

    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found.",
        )

    # Make sure current user belongs
    # to the expense group.
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

        item = await add_item_to_expense(
            db=db,
            expense_id=expense_id,
            name=payload.name,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            participants=payload.participants,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return ExpenseItemResponse(
        id=item.id,
        name=item.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=item.total_price,
        participants=[
            ExpenseItemParticipantResponse(
                user_id=participant.user_id,
                user_name=participant.user.name,
                share_amount=(
                    participant.share_amount
                ),
            )
            for participant in item.participants
        ],
    )