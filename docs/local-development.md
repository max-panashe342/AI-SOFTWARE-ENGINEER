# Local development

## Backend API and database

From `backend`, activate the existing virtual environment and start FastAPI:

```powershell
cd "D:\AI SOFTWARE ENGINEER\backend"
. .\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The SQLite database is created automatically at
`backend/data/engineering_workplace.db` when the application starts. SQLAlchemy
creates the tables and seeds `Frontend Engineering` by slug. The seed operation
is idempotent, so restarting the API does not add another copy.

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
