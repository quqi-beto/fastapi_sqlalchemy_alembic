import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserResponse]
    total: int
