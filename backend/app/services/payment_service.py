from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import PaymentAttempt
from app.models.settlement import Settlement
from app.models.user import User
from app.utils.upi import create_upi_uri


async def initiate_payment(
    *,
    db: AsyncSession,
    group_id: str,
    settlement_id: str,
    current_user_id: str,
    idempotency_key: str,
):
    # -------------------------------------------------
    # 1. Idempotency check
    # -------------------------------------------------

    existing_result = await db.execute(
        select(PaymentAttempt)
        .where(
            PaymentAttempt.payer_user_id
            == current_user_id,
            PaymentAttempt.idempotency_key
            == idempotency_key,
        )
    )

    existing_payment = (
        existing_result.scalar_one_or_none()
    )

    if existing_payment:
        return existing_payment, True

    # -------------------------------------------------
    # 2. Get settlement
    # -------------------------------------------------

    settlement_result = await db.execute(
        select(Settlement)
        .where(
            Settlement.id == settlement_id
        )
    )

    settlement = (
        settlement_result.scalar_one_or_none()
    )

    if not settlement:
        raise ValueError(
            "Settlement not found."
        )

    # -------------------------------------------------
    # 3. Verify payer
    # -------------------------------------------------
    if settlement.group_id != group_id:
        raise ValueError(
            "Settlement does not belong to this group."
        )
    
    if settlement.from_user_id != current_user_id:
        raise ValueError(
            "You are not authorized to pay this settlement."
        )

    # -------------------------------------------------
    # 4. Verify settlement state
    # -------------------------------------------------

    if settlement.status == "paid":
        raise ValueError(
            "Settlement is already paid."
        )

    if settlement.status != "pending":
        raise ValueError(
            f"Settlement cannot be paid in "
            f"its current state: {settlement.status}."
        )

    # -------------------------------------------------
    # 5. Get receiver
    # -------------------------------------------------

    receiver_result = await db.execute(
        select(User)
        .where(
            User.id == settlement.to_user_id,
            User.is_active.is_(True),
        )
    )

    receiver = (
        receiver_result.scalar_one_or_none()
    )

    if not receiver:
        raise ValueError(
            "Receiver not found."
        )

    # -------------------------------------------------
    # 6. Receiver UPI ID
    # -------------------------------------------------

    if not receiver.upi_id:
        raise ValueError(
            "Receiver has not configured a UPI ID."
        )

    # -------------------------------------------------
    # 7. Validate amount
    # -------------------------------------------------

    amount = Decimal(
        str(settlement.amount)
    ).quantize(
        Decimal("0.01")
    )

    if amount <= Decimal("0.00"):
        raise ValueError(
            "Settlement amount must be greater than zero."
        )

    # -------------------------------------------------
    # 8. Create payment reference
    # -------------------------------------------------

    payment = PaymentAttempt(
        group_id=settlement.group_id,
        settlement_id=settlement.id,
        payer_user_id=settlement.from_user_id,
        receiver_user_id=settlement.to_user_id,
        amount=amount,
        currency="INR",
        status="initiated",
        payment_method="upi",
        idempotency_key=idempotency_key,
    )

    db.add(payment)

    await db.flush()

    # -------------------------------------------------
    # 9. Generate UPI URI
    # -------------------------------------------------

    upi_uri = create_upi_uri(
        payee_vpa=receiver.upi_id,
        payee_name=receiver.name,
        amount=amount,
        transaction_reference=payment.id,
        note="SplitKaro settlement",
    )

    payment.upi_uri = upi_uri

    await db.commit()
    await db.refresh(payment)

    return payment, False