from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense import Expense
from app.models.expense_item import ExpenseItem
from app.models.expense_item_participant import (
    ExpenseItemParticipant,
)
from app.models.group_member import GroupMember
from app.utils.item_split_calculator import (
    calculate_item_total,
    validate_item_shares,
)


async def add_item_to_expense(
    db: AsyncSession,
    expense_id: str,
    name: str,
    quantity: Decimal,
    unit_price: Decimal,
    participants,
):
    result = await db.execute(
        select(Expense)
        .where(
            Expense.id == expense_id
        )
    )

    expense = result.scalar_one_or_none()

    if not expense:
        raise ValueError(
            "Expense not found."
        )

    participant_ids = [
        participant.user_id
        for participant in participants
    ]

    # Remove duplicates.
    participant_ids = list(
        dict.fromkeys(participant_ids)
    )

    # Make sure all users belong to the group.
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id
            == expense.group_id,
            GroupMember.user_id.in_(
                participant_ids
            ),
            GroupMember.is_active.is_(True),
        )
    )

    members = result.scalars().all()

    valid_ids = {
        member.user_id
        for member in members
    }

    if set(participant_ids) != valid_ids:
        raise ValueError(
            "All item participants must be "
            "active members of the group."
        )

    total_price = calculate_item_total(
        quantity,
        unit_price,
    )

    shares = {
        participant.user_id:
        participant.share_amount
        for participant in participants
    }

    validate_item_shares(
        total_price,
        shares,
    )

    item = ExpenseItem(
        expense_id=expense.id,
        name=name.strip(),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
    )

    db.add(item)

    await db.flush()

    for user_id, share_amount in shares.items():

        item_participant = (
            ExpenseItemParticipant(
                item_id=item.id,
                user_id=user_id,
                share_amount=share_amount,
            )
        )

        db.add(item_participant)

    await db.commit()

    result = await db.execute(
        select(ExpenseItem)
        .options(
            selectinload(
                ExpenseItem.participants
            ).selectinload(
                ExpenseItemParticipant.user
            )
        )
        .where(
            ExpenseItem.id == item.id
        )
    )

    return result.scalar_one()