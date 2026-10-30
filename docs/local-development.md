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
