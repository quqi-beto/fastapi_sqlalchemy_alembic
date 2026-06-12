import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── User Schemas ──
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


# ── Todo Schemas ──
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    user_id: uuid.UUID


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    id: uuid.UUID
    user_id: uuid.UUID
    date_completed: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodoList(BaseModel):
    todos: list[TodoResponse]
    total: int
