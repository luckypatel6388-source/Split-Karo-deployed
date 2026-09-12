from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.auth_account import AuthAccount
from app.models.user import User


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    result = await db.execute(
        select(User).where(
            User.email == email.lower()
        )
    )

    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    email: str,
    name: str,
    password: str,
) -> User:
    normalized_email = email.lower().strip()

    existing_user = await get_user_by_email(
        db,
        normalized_email,
    )

    if existing_user:
        raise ValueError(
            "An account with this email already exists."
        )

    user = User(
        email=normalized_email,
        name=name.strip(),
        is_active=True,
        is_verified=False,
    )

    db.add(user)

    await db.flush()

    auth_account = AuthAccount(
        user_id=user.id,
        provider="password",
        password_hash=hash_password(password),
    )

    db.add(auth_account)

    await db.commit()

    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:

    user = await get_user_by_email(
        db,
        email.strip().lower(),
    )

    if not user:
        return None

    if not user.is_active:
        return None

    result = await db.execute(
        select(AuthAccount).where(
            AuthAccount.user_id == user.id,
            AuthAccount.provider == "password",
        )
    )

    auth_account = result.scalar_one_or_none()

    if not auth_account:
        return None

    if not auth_account.password_hash:
        return None

    if not verify_password(
        password,
        auth_account.password_hash,
    ):
        return None

    return user