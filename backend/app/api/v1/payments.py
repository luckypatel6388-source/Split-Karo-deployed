from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
)
from app.services.payment_service import (
    initiate_payment,
)


router = APIRouter(
    prefix="/groups/{group_id}/payments",
    tags=["Payments"],
)


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
)
async def initiate_payment_endpoint(
    group_id: str,
    payload: PaymentInitiateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        payment, replay = await initiate_payment(
            db=db,
            group_id=group_id,
            settlement_id=payload.settlement_id,
            current_user_id=current_user.id,
            idempotency_key=payload.idempotency_key,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    receiver_result = await db.execute(
        select(User).where(
            User.id == payment.receiver_user_id
        )
    )

    receiver = receiver_result.scalar_one_or_none()

    return PaymentInitiateResponse(
        payment_id=payment.id,
        settlement_id=payment.settlement_id,
        payer_user_id=payment.payer_user_id,
        receiver_user_id=payment.receiver_user_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        payment_method=payment.payment_method,

        receiver_upi_id=(
            receiver.upi_id
            if receiver
            else None
        ),

        upi_uri=payment.upi_uri,

        message=(
            "Payment already initiated."
            if replay
            else
            "Payment initiated. "
            "Complete the payment in your UPI app."
        ),

        idempotent_replay=replay,
    )


"""from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
)
from app.services.payment_service import (
    initiate_payment,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
)
async def initiate_payment_endpoint(
    payload: PaymentInitiateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        payment, replay = await initiate_payment(
            db=db,

            settlement_id=payload.settlement_id,
            current_user_id=current_user.id,
            idempotency_key=payload.idempotency_key,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return PaymentInitiateResponse(
        payment_id=payment.id,
        settlement_id=payment.settlement_id,
        payer_user_id=payment.payer_user_id,
        receiver_user_id=payment.receiver_user_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        payment_method=payment.payment_method,
        receiver_upi_id=(
            payment.receiver.upi_id
            if payment.receiver
            else None
        ),
        upi_uri=payment.upi_uri,
        message=(
            "Payment already initiated."
            if replay
            else
            "Payment initiated. "
            "Complete the payment in your UPI app."
        ),
        idempotent_replay=replay,
    )"""