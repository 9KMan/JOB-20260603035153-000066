"""User CRUD endpoints."""
from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentSuperuser, CurrentUser, DBSession
from app.core.errors import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.security import hash_password

router = APIRouter()


@router.get("", response_model=list[UserRead], summary="List users")
async def list_users(
    db: DBSession, _admin: CurrentSuperuser, skip: int = 0, limit: int = 100
) -> list[User]:
    result = await db.execute(
        select(User).order_by(User.id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
async def create_user(db: DBSession, payload: UserCreate) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("A user with that email already exists")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead, summary="Get user by id")
async def get_user(db: DBSession, _admin: CurrentSuperuser, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return user


@router.patch("/me", response_model=UserRead, summary="Update current user")
async def update_me(
    db: DBSession, current_user: CurrentUser, payload: UserUpdate
) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        current_user.hashed_password = hash_password(data.pop("password"))
    for field, value in data.items():
        setattr(current_user, field, value)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(db: DBSession, _admin: CurrentSuperuser, user_id: int) -> None:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    await db.delete(user)
    await db.commit()
