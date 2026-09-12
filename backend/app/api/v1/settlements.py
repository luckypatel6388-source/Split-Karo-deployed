from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.settlement import (
    SettlementListResponse,
    SettlementResponse,
)

from app.schemas.settlement_record import (
    SettlementRecordResponse,
)

from app.services.group_service import (
    get_user_group,
)

from app.services.settlement_service import (
    calculate_group_settlements,
    create_optimized_settlements,
)

from app.services.settlement_record_service import (
    get_settlement,
)


router = APIRouter(
    prefix="/groups/{group_id}",
    tags=["Settlements"],
)


# =========================================================
# 1. PREVIEW OPTIMIZED SETTLEMENTS
# =========================================================

@router.get(
    "/settlements",
    response_model=SettlementListResponse,
)
async def get_settlements(
    group_id: str,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    settlements = await calculate_group_settlements(
        db=db,
        group_id=group_id,
    )

    return SettlementListResponse(
        group_id=group_id,
        settlements=[
            SettlementResponse(
                **settlement
            )
            for settlement in settlements
        ],
    )


# =========================================================
# 2. CREATE DATABASE SETTLEMENTS FROM OPTIMIZER
# =========================================================

@router.post(
    "/settlements/optimized",
    response_model=list[SettlementRecordResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_optimized_group_settlements(
    group_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    # -----------------------------------------------------
    # Verify current user belongs to group
    # -----------------------------------------------------

    group = await get_user_group(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    # -----------------------------------------------------
    # Create optimized settlement records
    # -----------------------------------------------------

    try:

        settlements = (
            await create_optimized_settlements(
                db=db,
                group_id=group_id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # -----------------------------------------------------
    # Convert database records to response
    # -----------------------------------------------------

    response = []

    for settlement in settlements:

        settlement = await get_settlement(
            db=db,
            settlement_id=settlement.id,
        )

        if not settlement:
            continue

        response.append(
            SettlementRecordResponse(
                id=settlement.id,
                group_id=settlement.group_id,

                from_user_id=(
                    settlement.from_user_id
                ),

                from_user_name=(
                    settlement.from_user.name
                ),

                to_user_id=(
                    settlement.to_user_id
                ),

                to_user_name=(
                    settlement.to_user.name
                ),

                amount=settlement.amount,

                status=settlement.status,

                payment_method=(
                    settlement.payment_method
                ),

                payment_reference=(
                    settlement.payment_reference
                ),

                paid_at=settlement.paid_at,
            )
        )

    return response