from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense import Expense
from app.models.expense_participant import (
    ExpenseParticipant,
)
from app.models.expense_item import (
    ExpenseItem,
)
from app.models.expense_item_participant import (
    ExpenseItemParticipant,
)
from app.models.expense_update_log import ExpenseUpdateLog


async def get_expense_with_details(
    db: AsyncSession,
    expense_id: str,
):

    result = await db.execute(
    select(Expense)
    .options(
        selectinload(
            Expense.payer
        ),

        selectinload(
            Expense.participants
        ).selectinload(
            ExpenseParticipant.user
        ),

        selectinload(
            Expense.items
        ).selectinload(
            ExpenseItem.participants
        ).selectinload(
            ExpenseItemParticipant.user
        ),
    )
    .where(
        Expense.id == expense_id
        )
    )

    return result.scalar_one_or_none()


async def get_expense_update_logs(
    db: AsyncSession,
    expense_id: str,
):
    result = await db.execute(
        select(ExpenseUpdateLog)
        .options(selectinload(ExpenseUpdateLog.editor))
        .where(ExpenseUpdateLog.expense_id == expense_id)
        .order_by(ExpenseUpdateLog.changed_at.desc())
    )
    return result.scalars().all()


async def update_expense_basic(
    db: AsyncSession,
    expense,
    title=None,
    description=None,
    amount=None,
    updated_by=None,
):

    update_log = ExpenseUpdateLog(
        expense_id=expense.id,
        updated_by=updated_by,
        previous_amount=expense.amount,
        updated_amount=amount if amount is not None else expense.amount,
        previous_title=expense.title,
        updated_title=title.strip() if title is not None else expense.title,
        previous_description=expense.description,
        updated_description=(
            description.strip() if description else None
        ) if description is not None else expense.description,
    )
    db.add(update_log)

    if title is not None:
        expense.title = title.strip()

    if description is not None:
        expense.description = (
            description.strip()
            if description
            else None
        )

    if amount is not None:
        expense.amount = amount

    await db.commit()
    await db.refresh(expense)

    return expense


async def delete_expense(
    db: AsyncSession,
    expense,
):

    await db.delete(expense)
    await db.commit()