

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payment_service import (
    initiate_payment,
)


async def prepare_bill_payment(
    db,
    *,
    group_id: str,
    settlement_id: str,
    current_user_id: str,
    idempotency_key: str,
):
    """
    Connects a confirmed bill/expense flow to payment.

    The bill must already have been reviewed and confirmed
    before this function is called.

    This function does not automatically charge the user.
    It prepares the payment attempt.
    """

    payment, replay = await initiate_payment(
        db=db,
        group_id=group_id,
        settlement_id=settlement_id,
        current_user_id=current_user_id,
        idempotency_key=idempotency_key,
    )

    # Safety check:
    # Make sure the settlement/payment belongs to
    # the group from which this function was called.
    if payment.group_id != group_id:
        raise ValueError(
            "Payment does not belong to this group."
        )

    return {
        "payment": payment,
        "idempotent_replay": replay,
    }