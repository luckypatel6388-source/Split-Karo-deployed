from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense_detail import (
    ExpenseDetailResponse,
    ExpenseItemDetail,
    ExpenseItemParticipantDetail,
    ExpenseParticipantDetail,
)
from app.services.expense_management_service import (
    get_expense_with_details,
)
from app.services.group_service import (
    get_user_group,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expense Details"],
)


@router.get(
    "/{expense_id}",
    response_model=ExpenseDetailResponse,
)
async def get_expense_detail(
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

    return ExpenseDetailResponse(
        id=expense.id,
        group_id=expense.group_id,
        title=expense.title,
        description=expense.description,
        amount=expense.amount, #type:ignore
        paid_by=expense.paid_by,
        payer_name=expense.payer.name,
        split_type=expense.split_type,
        participants=[
            ExpenseParticipantDetail(
                user_id=p.user_id,
                user_name=p.user.name,
                share_amount=p.share_amount,
            )
            for p in expense.participants
        ],
        items=[
            ExpenseItemDetail(
                id=item.id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                participants=[
                    ExpenseItemParticipantDetail(
                        user_id=ip.user_id,
                        user_name=ip.user.name,
                        share_amount=ip.share_amount,
                    )
                    for ip in item.participants
                ],
            )
            for item in expense.items
        ],
    )