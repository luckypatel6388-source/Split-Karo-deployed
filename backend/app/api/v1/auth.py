import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def create_session_token() -> tuple[str, str]:
    """
    Returns:

    raw_token
    token_hash
    """

    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    return raw_token, token_hash


def set_session_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite, #type:ignore
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await register_user(
            db=db,
            email=payload.email,
            name=payload.name,
            password=payload.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    raw_token, token_hash = create_session_token()

    session = Session(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        ).replace(tzinfo=None),
    )

    db.add(session)

    await db.commit()

    set_session_cookie(
        response,
        raw_token,
    )

    return AuthResponse(
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    raw_token, token_hash = create_session_token()

    session = Session(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        ).replace(tzinfo=None),
    )

    db.add(session)

    await db.commit()

    set_session_cookie(
        response,
        raw_token,
    )

    return AuthResponse(
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(
    response: Response,
    session_token: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # We will replace this with proper cookie extraction
    # in the next security refinement.

    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
    )

    return {
        "message": "Logged out successfully."
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(
        current_user
    )