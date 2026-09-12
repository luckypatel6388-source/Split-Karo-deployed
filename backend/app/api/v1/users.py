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
from app.schemas.group import GroupMemberResponse, GroupResponse
from app.schemas.user import (
    UpdateUPIRequest,
    UpdateUPIResponse,
)
from app.services.group_service import get_user_groups
from app.services.user_service import update_user_upi


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me/groups",
    response_model=list[GroupResponse],
    summary="List all groups the current user belongs to",
)
async def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    groups = await get_user_groups(
        db=db,
        user_id=current_user.id,
    )

    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            created_by=group.created_by,
            members=[
                GroupMemberResponse(
                    id=member.id,
                    user_id=member.user_id,
                    name=member.user.name,
                    email=member.user.email,
                    role=member.role,
                    is_active=member.is_active,
                )
                for member in group.members
            ],
        )
        for group in groups
    ]


@router.patch(
    "/me/upi",
    response_model=UpdateUPIResponse,
)
async def update_my_upi(
    payload: UpdateUPIRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await update_user_upi(
            db=db,
            user=current_user,
            upi_id=payload.upi_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UpdateUPIResponse(
        user_id=user.id,
        upi_id=user.upi_id,  # type: ignore[arg-type]
        upi_verified=user.upi_verified,
        message=(
            "UPI ID updated successfully. "
            "It is currently unverified."
        ),
    )
