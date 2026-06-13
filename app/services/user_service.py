import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user, checking for duplicate username/email."""
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    user = User(username=user_data.username, email=user_data.email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> list[User]:
    """Return all users ordered by creation date descending."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Return a single user by ID, or raise 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, user_data: UserCreate
) -> User:
    """Update an existing user's username and email."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = user_data.username
    user.email = user_data.email
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Delete a user by ID, or raise 404."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()
