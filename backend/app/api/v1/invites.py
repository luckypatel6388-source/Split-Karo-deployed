from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.group import Group
from app.models.group_invite import GroupInvite
from app.models.group_member import GroupMember
from app.models.user import User
from app.schemas.group import (
    InvitePreviewResponse,
    JoinGroupResponse,
)


router = APIRouter(
    prefix="/invites",
    tags=["Invites"],
)


@router.get(
    "/{token}",
    response_model=InvitePreviewResponse,
)
async def preview_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GroupInvite)
        .where(GroupInvite.token == token)
    )

    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found.",
        )

    if (
        invite.expires_at
        and invite.expires_at
        <= datetime.now(timezone.utc).replace(
            tzinfo=None
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invite has expired.",
        )

    if (
        invite.max_uses is not None
        and invite.use_count >= invite.max_uses
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invite has reached its usage limit.",
        )

    result = await db.execute(
        select(Group)
        .where(Group.id == invite.group_id)
    )

    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group no longer exists.",
        )

    return InvitePreviewResponse(
        group_id=group.id,
        group_name=group.name,
        group_description=group.description,
        expires_at=(
            invite.expires_at.isoformat()
            if invite.expires_at
            else None
        ),
    )


@router.post(
    "/{token}/join",
    response_model=JoinGroupResponse,
)
async def join_group(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GroupInvite)
        .where(GroupInvite.token == token)
    )

    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found.",
        )

    if (
        invite.expires_at
        and invite.expires_at
        <= datetime.now(timezone.utc).replace(
            tzinfo=None
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invite has expired.",
        )

    if (
        invite.max_uses is not None
        and invite.use_count >= invite.max_uses
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invite has reached its usage limit.",
        )

    result = await db.execute(
        select(Group)
        .where(Group.id == invite.group_id)
    )

    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    result = await db.execute(
        select(GroupMember)
        .where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == current_user.id,
        )
    )

    existing_member = result.scalar_one_or_none()

    if existing_member:
        if existing_member.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already a member of this group.",
            )

        existing_member.is_active = True

    else:
        member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role="member",
            is_active=True,
        )

        db.add(member)

    invite.use_count += 1

    await db.commit()

    return JoinGroupResponse(
        message="Successfully joined the group.",
        group_id=group.id,
        group_name=group.name,
    )