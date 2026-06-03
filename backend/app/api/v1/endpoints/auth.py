"""Authentication endpoints: login, refresh, me."""
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.errors import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserRead

router = APIRouter()


@router.post("/login", response_model=Token, summary="Obtain access and refresh tokens")
async def login(db: DBSession, form_data: OAuth2PasswordRequestForm = ...) -> Token:
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError("Invalid credentials")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh(db: DBSession, payload: TokenPayload) -> Token:
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception:
        raise UnauthorizedError("Invalid refresh token") from None
    if decoded.get("type") != "refresh":
        raise UnauthorizedError("Not a refresh token")
    user_id = int(decoded.get("sub"))
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not available")
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.get("/me", response_model=UserRead, summary="Current user profile")
async def read_me(current_user: CurrentUser) -> User:
    return current_user
