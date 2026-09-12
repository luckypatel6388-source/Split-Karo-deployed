from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense import (
    CreateExpenseRequest,
    ExpenseParticipantResponse,
    ExpenseResponse,
)
from app.services.expense_service import create_expense
from app.services.group_service import get_user_group


router = APIRouter(
    prefix="/groups/{group_id}/expenses",
    tags=["Expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_expense(
    group_id: str,
    payload: CreateExpenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    try:
        expense = await create_expense(
            db=db,
            group_id=group_id,
            title=payload.title,
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            split_type=payload.split_type,
            participant_user_ids=(
                payload.participant_user_ids
            ),
            custom_shares=payload.custom_shares,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    participants = [
        ExpenseParticipantResponse(
            user_id=participant.user_id,
            user_name=participant.user.name,
            share_amount=participant.share_amount,
        )
        for participant in expense.participants
    ]

    return ExpenseResponse(
        id=expense.id,
        group_id=expense.group_id,
        title=expense.title,
        description=expense.description,
        amount=expense.amount, #type:ignore
        paid_by=expense.paid_by,
        split_type=expense.split_type,
        participants=participants,
    )