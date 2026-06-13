import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserList, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, user_data)


@router.get("/", response_model=UserList)
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await user_service.get_users(db)
    return UserList(users=users, total=len(users))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID, user_data: UserCreate, db: AsyncSession = Depends(get_db)
):
    return await user_service.update_user(db, user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await user_service.delete_user(db, user_id)
