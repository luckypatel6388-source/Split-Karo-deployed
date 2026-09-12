from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense import Expense
from app.models.expense_participant import ExpenseParticipant
from app.models.group_member import GroupMember
from app.utils.expense_calculator import (
    calculate_equal_split,
    validate_custom_split,
)


async def create_expense(
    db: AsyncSession,
    group_id: str,
    title: str,
    description: str | None,
    amount: Decimal,
    paid_by: str,
    split_type: str,
    participant_user_ids: list[str],
    custom_shares=None,
) -> Expense:

    # Remove duplicates while preserving order.
    participant_user_ids = list(
        dict.fromkeys(participant_user_ids)
    )

    # Fetch active group members.
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id.in_(
                participant_user_ids
            ),
            GroupMember.is_active.is_(True),
        )
    )

    members = result.scalars().all()

    valid_user_ids = {
        member.user_id
        for member in members
    }

    requested_ids = set(
        participant_user_ids
    )

    invalid_users = (
        requested_ids - valid_user_ids
    )

    if invalid_users:
        raise ValueError(
            "One or more selected users are "
            "not active members of this group."
        )

    # Payer must be an active group member.
    if paid_by not in valid_user_ids:
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == paid_by,
                GroupMember.is_active.is_(True),
            )
        )

        payer_membership = result.scalar_one_or_none()

        if not payer_membership:
            raise ValueError(
                "The payer must be an active group member."
            )

    # Calculate shares.
    if split_type == "equal":

        shares = calculate_equal_split(
            amount=amount,
            participant_ids=participant_user_ids,
        )

    elif split_type == "custom":

        if not custom_shares:
            raise ValueError(
                "Custom split requires shares."
            )

        shares = {
            item.user_id: item.share_amount
            for item in custom_shares
        }

        if set(shares.keys()) != requested_ids:
            raise ValueError(
                "Custom shares must be provided "
                "for exactly the selected participants."
            )

        validate_custom_split(
            amount=amount,
            shares=shares,
        )

    else:
        raise ValueError(
            "Unsupported split type."
        )

    expense = Expense(
        group_id=group_id,
        paid_by=paid_by,
        title=title.strip(),
        description=description,
        amount=amount,
        split_type=split_type,
        expense_date=datetime.now(
            timezone.utc
        ).replace(tzinfo=None),
    )

    db.add(expense)

    await db.flush()

    for user_id in participant_user_ids:

        participant = ExpenseParticipant(
            expense_id=expense.id,
            user_id=user_id,
            share_amount=shares[user_id],
        )

        db.add(participant)

    await db.commit()

    result = await db.execute(
        select(Expense)
        .options(
            selectinload(
                Expense.participants
            ).selectinload(
                ExpenseParticipant.user
            )
        )
        .where(
            Expense.id == expense.id
        )
    )

    return result.scalar_one()