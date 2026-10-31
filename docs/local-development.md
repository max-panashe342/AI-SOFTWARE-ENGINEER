# Local development

## Backend API and database

From `backend`, activate the existing virtual environment and start FastAPI:

```powershell
cd "D:\AI SOFTWARE ENGINEER\backend"
. .\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The SQLite database is stored at
`backend/data/engineering_workplace.db`. Alembic owns the database schema;
FastAPI startup does not create or upgrade tables automatically.

For a fresh database, migrations must be applied before starting FastAPI:

```powershell
cd "D:\AI SOFTWARE ENGINEER\backend"
. .\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If FastAPI is started against a fresh database before the migration step, the
seed query will fail because the application tables do not exist. Do not solve
that by restoring `create_all()` or by running migrations implicitly at startup.

For a fresh local database, run the migration and seed workflow from `backend`:

```powershell
cd "D:\AI SOFTWARE ENGINEER\backend"
. .\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
```

The seed operation is idempotent, so it can be run repeatedly without adding
duplicate departments, competencies, assessments, versions or questions.

Useful migration commands are:

```powershell
alembic current
alembic history
alembic upgrade head
```

The existing database was adopted after a structural compatibility check using
`alembic stamp 0001_initial_schema`. Stamping records the baseline revision
without recreating tables or changing existing rows. Always back up the
database and verify its schema before stamping another pre-Alembic database.

Use a durable backup location outside this repository before adoption or
migration work. For example:

```powershell
$backupDirectory = Join-Path $env:USERPROFILE "AI-ERA-backups"
New-Item -ItemType Directory -Force $backupDirectory | Out-Null
Copy-Item ".\data\engineering_workplace.db" `
    (Join-Path $backupDirectory "engineering_workplace_before_migration.db")
```

Check the backup without modifying it:

```powershell
python -c "import sqlite3; p=r'C:\Users\<your-user>\AI-ERA-backups\engineering_workplace_before_migration.db'; c=sqlite3.connect('file:'+p+'?mode=ro', uri=True); print(c.execute('pragma integrity_check').fetchone()[0]); c.close()"
```

Never run `alembic downgrade base` against the adopted development database.
The baseline downgrade drops the application tables and is intended only for
disposable test databases. Keep durable backups outside the Git repository;
never copy the database or backups into source control.

The API is available at `http://localhost:8000`. The department directory
endpoint is:

```text
GET /api/departments
```

The API allows requests from the local Vite development origins
`http://localhost:5173` and `http://127.0.0.1:5173`.

## Authenticated profile API

The backend profile endpoints verify the Supabase access token with the
Supabase Auth user endpoint. No service-role key is used. Copy the empty
placeholders in `backend/.env` and set them locally with the public Supabase
project URL and publishable key before using authenticated profile requests:

```text
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
```

The protected endpoints are:

```text
GET /api/me
PATCH /api/me
```

The authenticated Supabase user UUID comes from the verified bearer token, not
from request body or query parameters. The first `GET /api/me` creates that
user's profile record; subsequent requests reuse it.

## Frontend API configuration

From `frontend`, start Vite:

```powershell
cd "D:\AI SOFTWARE ENGINEER\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
```

The frontend uses `http://localhost:8000` by default. To point it at another
API during local development, create `frontend/.env.local`:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Open `http://localhost:5173` and choose **Departments**, or open
`http://localhost:5173/departments` directly.

## Assessment definitions

The first Milestone 2 assessment definition is available through:

```text
GET /api/assessments
GET /api/assessments/frontend-engineering-foundations
```

Assessment versions are published independently from their assessment identity,
and questions reference explicit competencies. Candidate attempts, submitted
work, evaluation results, and placement recommendations are separate future
milestones.

The assessment records intentionally do not assign work to AI agents yet. Future
agent roles must use controlled backend services, have explicit permissions,
record whether an action was performed by an agent or a user, and preserve
evidence provenance. AI-generated work must remain distinguishable from a
candidate's independent demonstration.
