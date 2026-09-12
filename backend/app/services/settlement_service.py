from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession


from sqlalchemy import select

from app.models.settlement import Settlement
from app.services.balance_service import calculate_group_balances
from app.utils.settlement_optimizer import optimize_settlements


async def calculate_group_settlements(
    db: AsyncSession,
    group_id: str,
):

    balance_rows = await calculate_group_balances(
        db=db,
        group_id=group_id,
    )

    balances = {
        row["user_id"]: row["balance"]
        for row in balance_rows
    }

    user_names = {
        row["user_id"]: row["user_name"]
        for row in balance_rows
    }

    settlements = optimize_settlements(
        balances
    )

    result = []

    for settlement in settlements:

        amount = Decimal(
            str(
                settlement["amount"]
            )
        ).quantize(
            Decimal("0.01")
        )

        result.append(
            {
                "from_user_id": (
                    settlement[
                        "from_user_id"
                    ]
                ),
                "from_user_name": user_names[
                    settlement[
                        "from_user_id"
                    ]
                ],
                "to_user_id": (
                    settlement[
                        "to_user_id"
                    ]
                ),
                "to_user_name": user_names[
                    settlement[
                        "to_user_id"
                    ]
                ],
                "amount": amount,
            }
        )

    return result


async def create_optimized_settlements(
    db: AsyncSession,
    *,
    group_id: str,
):
    """
    Calculate optimized settlements and persist them
    as Settlement records.

    This creates the database records required by
    the payment system.
    """

    balance_rows = await calculate_group_balances(
        db=db,
        group_id=group_id,
    )

    balances = {
        row["user_id"]: row["balance"]
        for row in balance_rows
    }

    optimized = optimize_settlements(
        balances
    )

    created_settlements = []

    for item in optimized:

        from_user_id = item["from_user_id"]
        to_user_id = item["to_user_id"]

        amount = Decimal(
            str(item["amount"])
        ).quantize(
            Decimal("0.01")
        )

        if amount <= 0:
            continue

        # Prevent duplicate pending settlement
        # for the same direction and amount.
        result = await db.execute(
            select(Settlement).where(
                Settlement.group_id == group_id,
                Settlement.from_user_id == from_user_id,
                Settlement.to_user_id == to_user_id,
                Settlement.amount == amount,
                Settlement.status == "pending",
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            created_settlements.append(existing)
            continue

        settlement = Settlement(
            group_id=group_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=amount,
            status="pending",
            payment_method="upi",
        )

        db.add(settlement)
        created_settlements.append(settlement)

    await db.commit()

    for settlement in created_settlements:
        await db.refresh(settlement)

    return created_settlements

