from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.models.group_member import GroupMember


async def get_membership(
    db: AsyncSession,
    group_id: str,
    user_id: str,
) -> GroupMember | None:

    result = await db.execute(
        select(GroupMember)
        .where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
            GroupMember.is_active.is_(True),
        )
    )

    return result.scalar_one_or_none()


async def remove_member(
    db: AsyncSession,
    group: Group,
    target_user_id: str,
) -> bool:

    result = await db.execute(
        select(GroupMember)
        .where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == target_user_id,
            GroupMember.is_active.is_(True),
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        return False

    member.is_active = False

    await db.commit()

    return True


async def leave_group(
    db: AsyncSession,
    group: Group,
    user_id: str,
) -> bool:

    result = await db.execute(
        select(GroupMember)
        .where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == user_id,
            GroupMember.is_active.is_(True),
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        return False

    member.is_active = False

    await db.commit()

    return True