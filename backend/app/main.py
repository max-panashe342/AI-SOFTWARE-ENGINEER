from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.database import initialize_database
from app.routers.departments import router as departments_router
from app.routers.profile import router as profile_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments_router)
app.include_router(profile_router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "engineering-workplace-api"}
