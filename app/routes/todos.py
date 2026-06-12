import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Todo, User
from app.schemas import TodoCreate, TodoList, TodoResponse, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo_data: TodoCreate, db: AsyncSession = Depends(get_db)):
    # Verify user exists
    result = await db.execute(select(User).where(User.id == todo_data.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=todo_data.user_id,
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.get("/", response_model=TodoList)
async def get_todos(
    user_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)
):
    query = select(Todo).order_by(Todo.created_at.desc())
    if user_id:
        query = query.where(Todo.user_id == user_id)
    result = await db.execute(query)
    todos = result.scalars().all()
    return TodoList(todos=todos, total=len(todos))


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: uuid.UUID,
    todo_data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.completed is not None:
        todo.completed = todo_data.completed
        todo.date_completed = (
            datetime.now(timezone.utc) if todo_data.completed else None
        )

    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    await db.delete(todo)
    await db.commit()
