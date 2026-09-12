import hashlib

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.session import Session
from app.models.user import User


async def get_current_user(
    session_token: str | None = Cookie(
        default=None,
        alias="split_karo_session",
    ),
    db: AsyncSession = Depends(get_db),
) -> User:

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    result = await db.execute(
        select(Session)
        .where(Session.token_hash == token_hash)
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        )

    from datetime import datetime, timezone

    # Session timestamps are stored as naive UTC datetimes.
    if session.expires_at <= datetime.now(timezone.utc).replace(
        tzinfo=None
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired.",
        )

    result = await db.execute(
        select(User).where(
            User.id == session.user_id,
            User.is_active.is_(True),
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user