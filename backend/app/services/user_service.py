from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


async def update_user_upi(
    db: AsyncSession,
    *,
    user: User,
    upi_id: str,
) -> User:
    """
    Update the authenticated user's UPI ID.

    A changed UPI ID is considered unverified until
    a real verification mechanism is implemented.
    """

    upi_id = upi_id.strip().lower()

    # Basic UPI format validation
    if "@" not in upi_id:
        raise ValueError(
            "Invalid UPI ID. Expected format like name@bank."
        )

    if upi_id.startswith("@") or upi_id.endswith("@"):
        raise ValueError(
            "Invalid UPI ID."
        )

    # Check whether another user already owns this UPI ID
    result = await db.execute(
        select(User).where(
            User.upi_id == upi_id,
            User.id != user.id,
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError(
            "This UPI ID is already registered "
            "to another user."
        )

    user.upi_id = upi_id

    # We do not claim that the UPI ID is actually verified.
    user.upi_verified = False

    await db.commit()

    await db.refresh(user)

    return user