from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.group import (
    CreateGroupRequest,
    CreateInviteResponse,
    GroupMemberResponse,
    GroupResponse,
)
from app.services.group_service import (
    create_group,
    create_group_invite,
    get_group_with_members,
    get_user_group,
)


router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_group(
    payload: CreateGroupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await create_group(
        db=db,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )

    members = [
        GroupMemberResponse(
            id=member.id,
            user_id=member.user_id,
            name=member.user.name,
            email=member.user.email,
            role=member.role,
            is_active=member.is_active,
        )
        for member in group.members
    ]

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        members=members,
    )


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = await get_group_with_members(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    members = [
        GroupMemberResponse(
            id=member.id,
            user_id=member.user_id,
            name=member.user.name,
            email=member.user.email,
            role=member.role,
            is_active=member.is_active,
        )
        for member in group.members
    ]

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        members=members,
    )


@router.post(
    "/{group_id}/invite",
    response_model=CreateInviteResponse,
)
async def create_invite(
    group_id: str,
    current_user: User = Depends(get_current_user),
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

    if group.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the group admin can create invites.",
        )

    invite = await create_group_invite(
        db=db,
        group=group,
        user_id=current_user.id,
    )

    return CreateInviteResponse(
        token=invite.token,
        invite_url=f"/join/{invite.token}",
    )