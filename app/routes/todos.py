import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.todo import TodoCreate, TodoList, TodoResponse, TodoUpdate
from app.services import todo_service

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo_data: TodoCreate, db: AsyncSession = Depends(get_db)):
    return await todo_service.create_todo(db, todo_data)


@router.get("/", response_model=TodoList)
async def get_todos(
    user_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)
):
    todos, total = await todo_service.get_todos(db, user_id)
    return TodoList(todos=todos, total=total)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await todo_service.get_todo_by_id(db, todo_id)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: uuid.UUID,
    todo_data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await todo_service.update_todo(db, todo_id, todo_data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await todo_service.delete_todo(db, todo_id)
