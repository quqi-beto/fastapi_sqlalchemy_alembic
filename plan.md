# Plan: To Do API — FastAPI + Async SQLAlchemy + Alembic

**TL;DR:** Same To Do API (User + Todo CRUD) as the original plan, but with async SQLAlchemy (`asyncpg`/`aiosqlite`) and Alembic for all database migrations — dev, prod, and tests. Uses a layered architecture (controller → service → model) with per-entity files for clean scalability. Tests use a session-scoped SQLite DB with `alembic upgrade head` run once, then transaction rollback per test.

---

## Phase 1: Project Setup — *depends on nothing*

1. **Initialize project with `uv init`**
2. **Add dependencies**: `uv add fastapi uvicorn sqlalchemy asyncpg python-dotenv pydantic alembic`
3. **Add dev dependencies**: `uv add --dev pytest pytest-asyncio httpx aiosqlite`
4. **Create directories**: `app/`, `app/routes/`, `tests/`, `tests/test_routes/`
5. **Create `.env`** — async PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql+asyncpg://root:password@localhost:5432/todo_alembic_db
   ```
6. **Create `.env.test`** — async SQLite connection string:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./test.db
   ```

## Phase 2: Database & Config — *depends on Phase 1*

7. **Create `app/config.py`** — load `DATABASE_URL` from `.env` / `.env.test` using `python-dotenv`, expose a `Settings` class returning the database URL.

8. **Create `app/database.py`** — async SQLAlchemy setup:
   - `create_async_engine()` from `DATABASE_URL`
   - `async_sessionmaker` bound to the engine
   - `AsyncAttrs`-enabled declarative `Base`
   - `get_db()` async generator yielding sessions

9. **Initialize Alembic**:
   - Run `alembic init alembic` → creates `alembic/` directory and `alembic.ini`
   - Modify `alembic.ini` — point `sqlalchemy.url` to the **sync** PostgreSQL URL (Alembic uses sync):
     ```
     sqlalchemy.url = postgresql+psycopg2://root:password@localhost:5432/todo_alembic_db
     ```
   - Note: Alembic `env.py` will need `target_metadata = Base.metadata` imported from `app.database`

10. **Configure `alembic/env.py`**:
    - Import `Base` from `app.database` → set `target_metadata = Base.metadata`
    - Import `User` and `Todo` models so Alembic can detect them
    - Keep the default sync run_async — we use sync migration runner

## Phase 3: Models & Schemas (per-entity packages) — *depends on Phase 2*

11. **Create `app/models/` package** — one file per entity:
    - `app/models/__init__.py` — empty (no re-exports, import directly from submodules)
    - `app/models/user.py` — `User` ORM model: id (UUID PK), username (unique), email (unique), created_at
    - `app/models/todo.py` — `Todo` ORM model: id (UUID PK), title, description (optional), completed (default False), date_completed (optional), user_id (FK→User), created_at
    - Use `Mapped[]` annotations with `mapped_column()`
    - Add `async_` relationship attributes (e.g., `todos: Mapped[list["Todo"]] = relationship(...)`)
    - Cascade delete on user removal

12. **Create `app/schemas/` package** — one file per entity:
    - `app/schemas/__init__.py` — empty
    - `app/schemas/user.py` — `UserBase`, `UserCreate`, `UserResponse`, `UserList`
    - `app/schemas/todo.py` — `TodoBase`, `TodoCreate`, `TodoResponse`, `TodoUpdate`, `TodoList`
    - Add `model_config = ConfigDict(from_attributes=True)` for ORM compatibility

13. **Generate initial Alembic migration**:
    - Run `alembic revision --autogenerate -m "add user and todo tables"`
    - Verify the generated migration file in `alembic/versions/`
    - Run `alembic upgrade head` to apply

## Phase 4: Service Layer (business logic) — *depends on Phase 3*

14. **Create `app/services/` package**:
    - `app/services/__init__.py` — empty
    - `app/services/user_service.py` — `create_user`, `get_users`, `get_user_by_id`, `update_user`, `delete_user`
    - `app/services/todo_service.py` — `create_todo`, `get_todos`, `get_todo_by_id`, `update_todo`, `delete_todo`
    - Services handle all DB queries, validation, and commit/rollback
    - Routes delegate to services rather than doing DB work directly

## Phase 5: API Routes (thin controllers) — *depends on Phase 4*

15. **Create `app/routes/users.py`** — thin async CRUD endpoints:
    - `POST /users` — delegate to `user_service.create_user()`
    - `GET /users` — delegate to `user_service.get_users()`
    - `GET /users/{id}` — delegate to `user_service.get_user_by_id()`
    - `PUT /users/{id}` — delegate to `user_service.update_user()`
    - `DELETE /users/{id}` — delegate to `user_service.delete_user()`

16. **Create `app/routes/todos.py`** — thin async CRUD endpoints, same delegation pattern.

## Phase 6: Application Entry Point — *depends on Phase 5*

17. **Create `app/main.py`**:
    - FastAPI app with `lifespan` context manager (replaces deprecated `on_event`)
    - Lifespan startup: just log "starting up" — **no** `Base.metadata.create_all()`
    - Register both routers
    - `root` health-check endpoint
    - Note: Tables are created by Alembic, not by the app itself

## Phase 7: Testing Infrastructure — *depends on Phase 6* (*parallel with Phase 5*)

18. **Create `tests/conftest.py`** — async fixtures:
    - **`setup_test_database` (session scope, sync)**: Create a single SQLite file-based DB (`sqlite:///./test.db`), run `alembic upgrade head` via sync subprocess, yield, then cleanup.
    - **`async_engine` (session async)**: Create async engine for SQLite (`sqlite+aiosqlite:///./test.db`), yield, dispose.
    - **`session` (function async)**: Begin a connection, start a transaction, yield an `AsyncSession` bound to that connection, rollback on teardown. This gives per-test isolation without re-running migrations.
    - **`client`**: Create `AsyncClient` with `AsyncClient(app=app, base_url="http://test")`, override `get_db` dependency to inject the test session.

    *Key implementation detail for Alembic in tests:* Alembic uses sync SQLAlchemy, so `setup_test_database` runs it synchronously once at session scope via `alembic.config.main(argv=["upgrade", "head"])`.

## Phase 8: Unit Tests — *depends on Phase 7*

19. **Create `tests/test_models.py`** — test model instantiation, defaults, relationships
20. **Create `tests/test_schemas.py`** — test Pydantic validation
21. **Create `tests/test_database.py`** — test async DB connection and session
22. **Create `tests/test_routes/test_users.py`** — test all user endpoints
23. **Create `tests/test_routes/test_todos.py`** — test all todo endpoints

## Phase 9: Verification — *depends on Phase 8*

24. Run `uv run pytest -v` — all tests pass
25. Run `alembic upgrade head` — applies migrations to PostgreSQL
26. Start server: `uv run uvicorn app.main:app --reload`
27. Test manually in Swagger UI (`/docs`)

---

## Files to create

| File | Purpose |
|------|---------|
| `pyproject.toml` | `uv init` auto-created |
| `.env` | Async PostgreSQL URL |
| `.env.test` | Async SQLite URL |
| `alembic.ini` | Alembic config (sync URL) |
| `alembic/env.py` | Alembic env with `Base.metadata` |
| `alembic/script.py.mako` | Migration template (auto) |
| `alembic/versions/` | Migration version files |
| `app/__init__.py` | Package marker |
| `app/config.py` | Settings from `.env` |
| `app/database.py` | Async engine, session, Base |
| `app/models/__init__.py` | Empty package marker |
| `app/models/user.py` | User ORM model |
| `app/models/todo.py` | Todo ORM model |
| `app/schemas/__init__.py` | Empty package marker |
| `app/schemas/user.py` | User Pydantic schemas |
| `app/schemas/todo.py` | Todo Pydantic schemas |
| `app/services/__init__.py` | Empty package marker |
| `app/services/user_service.py` | User business logic |
| `app/services/todo_service.py` | Todo business logic |
| `app/main.py` | FastAPI app entry point |
| `app/routes/__init__.py` | Package marker |
| `app/routes/users.py` | User CRUD (thin controller — delegates to service) |
| `app/routes/todos.py` | Todo CRUD (thin controller — delegates to service) |
| `tests/__init__.py` | Package marker |
| `tests/conftest.py` | Async fixtures + Alembic setup |
| `tests/test_models.py` | Model tests |
| `tests/test_schemas.py` | Schema tests |
| `tests/test_database.py` | DB connection tests |
| `tests/test_routes/__init__.py` | Package marker |
| `tests/test_routes/test_users.py` | User endpoint tests |
| `tests/test_routes/test_todos.py` | Todo endpoint tests |

## Key differences from original plan

| Original | New (`plan2.md`) |
|----------|-----------------|
| Sync SQLAlchemy (`psycopg2-binary`) | Async SQLAlchemy (`asyncpg`) |
| `Base.metadata.create_all()` on startup | Alembic migrations |
| No Alembic | Full Alembic pipeline |
| Sync test fixtures | Async test fixtures |
| Per-test table create/drop | Session-scoped Alembic + transaction rollback |
| PostgreSQL for tests | SQLite for tests |
| Business logic in routes | **Service layer** — routes are thin controllers |
| Monolithic `models.py` / `schemas.py` | **Per-entity files** under `models/`, `schemas/`, `services/` |

## Verification Checklist

- ✅ `uv run pytest -v` — 41 tests pass
- ✅ `alembic history` — shows migration history
- ✅ `alembic upgrade head` on fresh PostgreSQL — tables created
- ✅ `alembic downgrade -1` — tables removed, rollback verified
- ✅ Swagger UI (`/docs`) — full CRUD working via async endpoints
- ✅ README.md — setup, API reference, test strategy documented

## Decisions

- **Async SQLAlchemy** with `asyncpg` (prod) and `aiosqlite` (tests)
- **Sync Alembic runner** (standard approach)
- **Session-scoped test DB** — `alembic upgrade head` runs once, transaction rollback per test
- No auth, no pagination (MVP scope)
- `uv` for project/dependency management
- Cascade delete on User → deletes all their Todos
- UUID primary keys for models
- Timezone-aware timestamps (UTC)
- **Layered architecture**: routes (thin controllers) → services (business logic) → models/schemas (data layer)
- **Per-entity files** under `models/`, `schemas/`, `services/` packages for clean separation and scalability
- **Empty `__init__.py` files** (no re-exports) — import directly from entity files
