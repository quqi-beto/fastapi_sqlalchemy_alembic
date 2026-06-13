Plan: To Do API with FastAPI, PostgreSQL, SQLAlchemy

TL;DR: Build a simple To Do API with full CRUD for Users and To Dos using uv for project management. Each user has many To Dos. Uses a layered architecture (controller → service → model) with per-entity files for clean scalability. Includes comprehensive pytest unit tests for models, schemas, and all API endpoints. Tests use a separate test database to keep data isolated.

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

Phase 3: Models & Schemas (per-entity packages) — depends on Phase 2

8. Create app/models/ (package) — one file per entity
   - app/models/__init__.py — empty (no re-exports, import directly from submodules)
   - app/models/user.py — User ORM model
   - app/models/todo.py — Todo ORM model with FK to User

9. Create app/schemas/ (package) — one file per entity
   - app/schemas/__init__.py — empty
   - app/schemas/user.py — Pydantic models (UserBase, UserCreate, UserResponse, UserList)
   - app/schemas/todo.py — Pydantic models (TodoBase, TodoCreate, TodoUpdate, TodoResponse, TodoList)

Phase 4: Service Layer (business logic) — depends on Phase 3

10. Create app/services/ (package)
    - app/services/__init__.py — empty
    - app/services/user_service.py — create_user, get_users, get_user_by_id, update_user, delete_user
    - app/services/todo_service.py — create_todo, get_todos, get_todo_by_id, update_todo, delete_todo

Phase 5: API Routes (thin controllers) — depends on Phase 4

11. Create app/routes/users.py — thin endpoints that delegate to user_service
    (POST, GET all, GET one, PUT, DELETE)

12. Create app/routes/todos.py — thin endpoints that delegate to todo_service
    (POST, GET all, GET one, PUT, DELETE)

Phase 6: Application Entry Point — depends on Phase 5

13. Create app/main.py — FastAPI app setup, register routers, auto-create tables on startup

Phase 7: Testing Infrastructure — depends on Phase 6 (can start in parallel with Phase 5)

14. Create tests/conftest.py — pytest fixtures for test database, TestClient, auto table creation/teardown

Phase 8: Unit Tests — depends on Phase 7

15. Create tests/test\_models.py — test model instantiation, default values, relationships

16. Create tests/test\_schemas.py — test Pydantic validation

17. Create tests/test\_database.py — test DB connection and session

18. Create tests/test\_routes/test\_users.py — test all user endpoints (create, read, update, delete)

19. Create tests/test\_routes/test\_todos.py — test all todo endpoints (create, read, update, delete)

Phase 9: Verification — depends on Phase 8

20. Run uv run pytest to verify all tests pass

21. Start server with uv run uvicorn app.main:app --reload and test manually in Swagger UI (/docs)

Relevant files to create

pyproject.toml — auto-created by uv init

.env — production PostgreSQL connection string

.env.test — test PostgreSQL connection string (separate DB)

app/main.py — FastAPI app and router registration

app/database.py — SQLAlchemy setup (engine, SessionLocal, Base)

app/models/__init__.py — empty package marker

app/models/user.py — User ORM model

app/models/todo.py — Todo ORM model with FK to User

app/schemas/__init__.py — empty package marker

app/schemas/user.py — Pydantic request/response models for User

app/schemas/todo.py — Pydantic request/response models for Todo

app/services/__init__.py — empty package marker

app/services/user_service.py — User business logic

app/services/todo_service.py — Todo business logic

app/config.py — configuration from .env

app/routes/users.py — User CRUD endpoints (thin controllers)

app/routes/todos.py — Todo CRUD endpoints (thin controllers)

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

Layered architecture: routes (thin controllers) → services (business logic) → models/schemas (data layer)

Per-entity files under models/, schemas/, services/ packages for clean separation and scalability

Empty __init__.py files (no re-exports) — import directly from entity files