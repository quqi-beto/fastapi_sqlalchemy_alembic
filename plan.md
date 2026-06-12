Plan: To Do API with FastAPI, PostgreSQL, SQLAlchemy

TL;DR: Build a simple To Do API with full CRUD for Users and To Dos using uv for project management. Each user has many To Dos. Includes comprehensive pytest unit tests for models, schemas, and all API endpoints. Tests use a separate test database to keep data isolated.

Steps

Phase 1: Project Setup (using uv) — depends on nothing

Initialize project with uv init

Add dependencies: uv add fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic

Add dev dependencies: uv add --dev pytest pytest-asyncio httpx

Create project directories (app/, tests/, app/routes/, tests/test\_routes/)

Create .env (production DB) and .env.test (test DB)

Phase 2: Database Configuration — depends on Phase 1

6. Create app/config.py — load DB URLs from .env variables

7. Create app/database.py — SQLAlchemy engine, SessionLocal, declarative Base

Phase 3: Models & Schemas — depends on Phase 2

8. Create app/models.py — User and Todo ORM models with relationships

9. Create app/schemas.py — Pydantic models (UserBase, UserCreate, UserResponse, etc.)

Phase 4: API Routes — depends on Phase 3

10. Create app/routes/users.py — User CRUD endpoints (POST, GET all, GET one, PUT, DELETE)

11. Create app/routes/todos.py — Todo CRUD endpoints (POST, GET all, GET one, PUT, DELETE)

Phase 5: Application Entry Point — depends on Phase 4

12. Create app/main.py — FastAPI app setup, register routers, auto-create tables on startup

Phase 6: Testing Infrastructure — depends on Phase 5 (can start in parallel with Phase 4)

13. Create tests/conftest.py — pytest fixtures for test database, TestClient, auto table creation/teardown

Phase 7: Unit Tests — depends on Phase 6

14. Create tests/test\_models.py — test model instantiation, default values, relationships

15. Create tests/test\_schemas.py — test Pydantic validation

16. Create tests/test\_database.py — test DB connection and session

17. Create tests/test\_routes/test\_users.py — test all user endpoints (create, read, update, delete)

18. Create tests/test\_routes/test\_todos.py — test all todo endpoints (create, read, update, delete)

Phase 8: Verification — depends on Phase 7

19. Run uv run pytest to verify all tests pass

20. Start server with uv run uvicorn app.main:app --reload and test manually in Swagger UI (/docs)

Relevant files to create

pyproject.toml — auto-created by uv init

.env — production PostgreSQL connection string

.env.test — test PostgreSQL connection string (separate DB)

app/main.py — FastAPI app and router registration

app/database.py — SQLAlchemy setup (engine, SessionLocal, Base)

app/models.py — User and Todo SQLAlchemy ORM models

app/schemas.py — Pydantic request/response models

app/config.py — configuration from .env

app/routes/users.py — User CRUD endpoints

app/routes/todos.py — Todo CRUD endpoints

tests/conftest.py — pytest fixtures

tests/test\_models.py — model tests

tests/test\_schemas.py — schema validation tests

tests/test\_database.py — database tests

tests/test\_routes/test\_users.py — user endpoint tests

tests/test\_routes/test\_todos.py — todo endpoint tests

Verification

Run uv run pytest — all tests pass

Create a user via POST /users in Swagger UI → 201 response

Create a todo linked to that user → 201 response

Update todo to mark completed → date\_completed is auto-set

Delete user → cascading delete removes user's todos

Verify PostgreSQL has User and Todo tables

Decisions

Using uv for project management and dependency management

Pytest with pytest-asyncio for async tests

httpx TestClient for testing FastAPI endpoints

Separate test database (.env.test) to isolate test data

No authentication for MVP

No pagination for MVP

SQLAlchemy ORM for type safety