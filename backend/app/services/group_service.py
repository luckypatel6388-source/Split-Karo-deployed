from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.group import Group
from app.models.group_invite import GroupInvite
from app.models.group_member import GroupMember
from app.utils.invite import generate_invite_token


async def create_group(
    db: AsyncSession,
    user_id: str,
    name: str,
    description: str | None,
) -> Group:

    group = Group(
        name=name.strip(),
        description=description,
        created_by=user_id,
    )

    db.add(group)

    await db.flush()

    member = GroupMember(
        group_id=group.id,
        user_id=user_id,
        role="admin",
    )

    db.add(member)

    await db.commit()

    result = await db.execute(
        select(Group)
        .options(
            selectinload(Group.members)
        )
        .where(Group.id == group.id)
    )

    return result.scalar_one()


async def get_user_group(
    db: AsyncSession,
    group_id: str,
    user_id: str,
) -> Group | None:

    result = await db.execute(
        select(Group)
        .join(GroupMember)
        .where(
            Group.id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.is_active.is_(True),
        )
    )

    return result.scalar_one_or_none()


async def get_group_with_members(
    db: AsyncSession,
    group_id: str,
    user_id: str,
) -> Group | None:

    result = await db.execute(
        select(Group)
        .join(GroupMember)
        .options(
            selectinload(Group.members)
            .selectinload(GroupMember.user)
        )
        .where(
            Group.id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.is_active.is_(True),
        )
    )

    return result.scalar_one_or_none()


async def get_user_groups(
    db: AsyncSession,
    user_id: str,
) -> list[Group]:
    """Return all active groups the given user belongs to,
    with members eagerly loaded (needed by GroupResponse)."""

    result = await db.execute(
        select(Group)
        .join(
            GroupMember,
            GroupMember.group_id == Group.id,
        )
        .options(
            selectinload(Group.members)
            .selectinload(GroupMember.user)
        )
        .where(
            GroupMember.user_id == user_id,
            GroupMember.is_active.is_(True),
        )
        .order_by(Group.created_at.desc())
    )

    return list(result.scalars().all())


async def create_group_invite(
    db: AsyncSession,
    group: Group,
    user_id: str,
) -> GroupInvite:

    token = generate_invite_token()

    invite = GroupInvite(
        group_id=group.id,
        created_by=user_id,
        token=token,
    )

    db.add(invite)

    await db.commit()
    await db.refresh(invite)

    return invite