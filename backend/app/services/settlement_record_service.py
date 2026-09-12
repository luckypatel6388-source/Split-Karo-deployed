from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.settlement import Settlement
from app.models.group_member import GroupMember
from app.services.balance_service import (
    calculate_group_balances,
)
from app.utils.settlement_validator import (
    validate_settlement_amount,
    validate_settlement_against_balance,
    validate_settlement_users,
)


async def get_group_members_map(
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

    members = result.scalars().unique().all()

    return {
        member.user_id: member.user
        for member in members
    }


async def create_settlement(
    db: AsyncSession,
    group_id: str,
    from_user_id: str,
    to_user_id: str,
    amount: Decimal,
    payment_method: str | None = None,
):
    validate_settlement_users(
        from_user_id,
        to_user_id,
    )

    validate_settlement_amount(amount)

    members = await get_group_members_map(
        db=db,
        group_id=group_id,
    )

    if from_user_id not in members:
        raise ValueError(
            "Payer is not a member of this group."
        )

    if to_user_id not in members:
        raise ValueError(
            "Receiver is not a member of this group."
        )

    balances = await calculate_group_balances(
        db=db,
        group_id=group_id,
    )

    payer_balance = next(
        (
            row["balance"]
            for row in balances
            if row["user_id"] == from_user_id
        ),
        Decimal("0"),
    )

    # Negative means the user owes money.
    actual_owed = max(
        -Decimal(str(payer_balance)),
        Decimal("0"),
    )

    validate_settlement_against_balance(
        amount=amount,
        actual_owed=actual_owed,
    )

    settlement = Settlement(
        group_id=group_id,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        amount=amount,
        status="pending",
        payment_method=payment_method,
    )

    db.add(settlement)

    await db.commit()
    await db.refresh(settlement)

    return settlement


async def mark_settlement_paid(
    db: AsyncSession,
    settlement: Settlement,
    payment_reference: str | None = None,
):
    if settlement.status == "paid":
        raise ValueError(
            "Settlement is already marked as paid."
        )

    settlement.status = "paid"

    settlement.payment_reference = (
        payment_reference
    )

    settlement.paid_at = datetime.now(
        timezone.utc
    )

    await db.commit()
    await db.refresh(settlement)

    return settlement


async def get_settlement(
    db: AsyncSession,
    settlement_id: str,
):
    result = await db.execute(
        select(Settlement)
        .options(
            selectinload(
                Settlement.from_user
            ),
            selectinload(
                Settlement.to_user
            ),
        )
        .where(
            Settlement.id == settlement_id
        )
    )

    return result.scalar_one_or_none()