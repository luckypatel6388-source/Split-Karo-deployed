from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.schemas.settlement_record import (
    CreateSettlementRequest,
    MarkSettlementPaidRequest,
    SettlementRecordResponse,
)
from app.services.group_service import (
    get_user_group,
)
from app.services.settlement_record_service import (
    create_settlement,
    get_settlement,
    mark_settlement_paid,
)


router = APIRouter(
    prefix="/groups/{group_id}/settlements",
    tags=["Settlement Management"],
)


def settlement_response(
    settlement,
):
    return SettlementRecordResponse(
        id=settlement.id,
        group_id=settlement.group_id,
        from_user_id=settlement.from_user_id,
        from_user_name=settlement.from_user.name,
        to_user_id=settlement.to_user_id,
        to_user_name=settlement.to_user.name,
        amount=settlement.amount,
        status=settlement.status,
        payment_method=settlement.payment_method,
        payment_reference=(
            settlement.payment_reference
        ),
        paid_at=settlement.paid_at,
    )


@router.post(
    "",
    response_model=SettlementRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_settlement(
    group_id: str,
    payload: CreateSettlementRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group.",
        )

    try:
        settlement = await create_settlement(
            db=db,
            group_id=group_id,
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            amount=payload.amount,
            payment_method=(
                payload.payment_method
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    settlement = await get_settlement(
        db=db,
        settlement_id=settlement.id,
    )

    return settlement_response(
        settlement
    )


@router.patch(
    "/{settlement_id}/paid",
    response_model=SettlementRecordResponse,
)
async def complete_settlement(
    group_id: str,
    settlement_id: str,
    payload: MarkSettlementPaidRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group.",
        )

    settlement = await get_settlement(
        db=db,
        settlement_id=settlement_id,
    )

    if not settlement:
        raise HTTPException(
            status_code=404,
            detail="Settlement not found.",
        )

    if settlement.group_id != group_id:
        raise HTTPException(
            status_code=404,
            detail="Settlement not found.",
        )

    try:
        settlement = await mark_settlement_paid(
            db=db,
            settlement=settlement,
            payment_reference=(
                payload.payment_reference
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return settlement_response(
        settlement
    )


@router.get(
    "/records/{settlement_id}",
    response_model=SettlementRecordResponse,
)
async def get_settlement_record(
    group_id: str,
    settlement_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group.",
        )

    settlement = await get_settlement(
        db=db,
        settlement_id=settlement_id,
    )

    if not settlement:
        raise HTTPException(
            status_code=404,
            detail="Settlement not found.",
        )

    if settlement.group_id != group_id:
        raise HTTPException(
            status_code=404,
            detail="Settlement not found.",
        )

    return settlement_response(
        settlement
    )