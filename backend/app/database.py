from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "engineering_workplace.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def initialize_database() -> None:
    from app.models import Department, UserProfile

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if session.query(Department).filter_by(slug="frontend-engineering").first() is None:
            session.add(
                Department(
                    name="Frontend Engineering",
                    slug="frontend-engineering",
                    description="Build accessible, thoughtful interfaces that make complex work feel simple.",
                    status="active",
                )
            )
            session.commit()
