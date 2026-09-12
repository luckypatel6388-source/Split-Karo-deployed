from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.group_member import GroupMember
from app.utils.balance_calculator import calculate_balances

from app.models.settlement import Settlement

async def get_group_expenses(
    db: AsyncSession,
    group_id: str,
):
    result = await db.execute(
        select(Expense)
        .options(
            selectinload(
                Expense.participants
            ).selectinload(
                ExpenseParticipant.user
            ),
            selectinload(
                Expense.payer
            ),
        )
        .where(
            Expense.group_id == group_id
        )
        .order_by(
            Expense.created_at.desc()
        )
    )

    return result.scalars().unique().all()


async def get_group_members(
    db: AsyncSession,
    group_id: str,
):
    result = await db.execute(
        select(GroupMember)
        .options(
            selectinload(
                GroupMember.user
            )
        )
        .where(
            GroupMember.group_id == group_id,
            GroupMember.is_active.is_(True),
        )
    )

    return result.scalars().unique().all()

async def get_group_settlements(
    db: AsyncSession,
    group_id: str,
):
    result = await db.execute(
        select(Settlement)
        .where(
            Settlement.group_id == group_id
        )
    )

    return result.scalars().all()

async def calculate_group_balances(
    db: AsyncSession,
    group_id: str,
):

    expenses = await get_group_expenses(
        db=db,
        group_id=group_id,
    )

    members = await get_group_members(
        db=db,
        group_id=group_id,
    )

    settlements = await get_group_settlements(
    db=db,
    group_id=group_id,
    )

    balances = calculate_balances(
        expenses=expenses,
        settlements=settlements,
    )

    result = []

    for member in members:

        balance = balances.get(
            member.user_id,
            0,
        )

        result.append(
            {
                "user_id": member.user_id,
                "user_name": member.user.name,
                "balance": balance,
            }
        )

    return result