from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.balance import (
    ExpenseHistoryItemResponse,
    ExpenseHistoryParticipantResponse,
    GroupBalanceResponse,
    UserBalanceResponse,
)
from app.services.balance_service import (
    calculate_group_balances,
    get_group_expenses,
)
from app.services.group_service import get_user_group


router = APIRouter(
    prefix="/groups/{group_id}",
    tags=["Balances"],
)


@router.get(
    "/balances",
    response_model=GroupBalanceResponse,
)
async def get_balances(
    group_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found.",
        )

    balances = await calculate_group_balances(
        db=db,
        group_id=group_id,
    )

    return GroupBalanceResponse(
        group_id=group_id,
        balances=[
            UserBalanceResponse(
                **balance
            )
            for balance in balances
        ],
    )


@router.get(
    "/expenses",
    response_model=list[
        ExpenseHistoryItemResponse
    ],
)
async def get_expense_history(
    group_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found.",
        )

    expenses = await get_group_expenses(
        db=db,
        group_id=group_id,
    )

    return [
        ExpenseHistoryItemResponse(
            expense_id=expense.id,
            title=expense.title,
            amount=expense.amount, #type:ignore
            paid_by=expense.paid_by,
            payer_name=expense.payer.name,
            split_type=expense.split_type,
            participants=[
                ExpenseHistoryParticipantResponse(
                    user_id=p.user_id,
                    user_name=p.user.name,
                    share_amount=p.share_amount,
                )
                for p in expense.participants
            ],
        )
        for expense in expenses
    ]