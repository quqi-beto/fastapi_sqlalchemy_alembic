from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import todos, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing to do — Alembic handles table creation
    yield
    # Shutdown: nothing to clean up


app = FastAPI(title="To Do API", version="1.0.0", lifespan=lifespan)

app.include_router(users.router)
app.include_router(todos.router)


@app.get("/")
async def root():
    return {"message": "To Do API is running"}
