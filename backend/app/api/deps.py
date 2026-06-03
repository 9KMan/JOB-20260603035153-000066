"""Shared FastAPI dependencies (DB session, current user, etc.)."""
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.core.security import decode_token
from app.database import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    db: DBSession, token: TokenDep
) -> User:
    if not token:
        raise UnauthorizedError("Not authenticated")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise UnauthorizedError("Token missing subject")
        user_id = int(user_id_raw)
    except (JWTError, ValueError):
        raise UnauthorizedError("Invalid or expired token") from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges"
        )
    return current_user


CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]
