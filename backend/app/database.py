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
    from datetime import datetime, timezone

    from app.models import (
        Assessment,
        AssessmentQuestion,
        AssessmentVersion,
        Competency,
        Department,
        UserProfile,
    )

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

        department = session.query(Department).filter_by(slug="frontend-engineering").one()
        competency_definitions = [
            (
                "semantic-html-accessibility",
                "Semantic HTML and accessibility",
                "Build interfaces with meaningful structure, keyboard access, and inclusive interaction patterns.",
            ),
            (
                "responsive-css",
                "Responsive CSS",
                "Create layouts that remain usable and coherent across viewport sizes.",
            ),
            (
                "react-typescript",
                "React and TypeScript",
                "Structure maintainable React components with clear, type-safe data flow.",
            ),
        ]
        competencies: dict[str, Competency] = {}
        for slug, name, description in competency_definitions:
            competency = session.query(Competency).filter_by(department_id=department.id, slug=slug).first()
            if competency is None:
                competency = Competency(
                    department_id=department.id,
                    slug=slug,
                    name=name,
                    description=description,
                )
                session.add(competency)
                session.flush()
            competencies[slug] = competency

        assessment = session.query(Assessment).filter_by(slug="frontend-engineering-foundations").first()
        if assessment is None:
            assessment = Assessment(
                department_id=department.id,
                slug="frontend-engineering-foundations",
                name="Frontend Engineering Foundations",
                description="Demonstrate practical frontend engineering fundamentals through accessible, responsive, typed interface work.",
            )
            session.add(assessment)
            session.flush()

        version = (
            session.query(AssessmentVersion)
            .filter_by(assessment_id=assessment.id, version_number=1)
            .first()
        )
        if version is None:
            version = AssessmentVersion(
                assessment_id=assessment.id,
                version_number=1,
                status="published",
                instructions=(
                    "Complete each practical task using the provided requirements. "
                    "Explain important implementation decisions and submit work you can defend."
                ),
                time_limit_minutes=90,
                published_at=datetime.now(timezone.utc),
            )
            session.add(version)
            session.flush()

            questions = [
                AssessmentQuestion(
                    assessment_version_id=version.id,
                    competency_id=competencies["semantic-html-accessibility"].id,
                    position=1,
                    type="practical_task",
                    prompt="Create an accessible profile card for a user with a name, role, and contact action.",
                    instructions="Use semantic elements and ensure the contact action is keyboard accessible.",
                    language="tsx",
                    max_score=10,
                ),
                AssessmentQuestion(
                    assessment_version_id=version.id,
                    competency_id=competencies["responsive-css"].id,
                    position=2,
                    type="practical_task",
                    prompt="Make the profile card adapt from a two-column desktop layout to a readable mobile layout.",
                    instructions="Describe the responsive behavior and the CSS strategy you chose.",
                    language="css",
                    max_score=10,
                ),
                AssessmentQuestion(
                    assessment_version_id=version.id,
                    competency_id=competencies["react-typescript"].id,
                    position=3,
                    type="coding",
                    prompt="Implement a typed React component that renders the profile card from a supplied profile object.",
                    instructions="Keep the component focused and make the profile data type explicit.",
                    starter_code="type Profile = { name: string; role: string; email: string }",
                    language="tsx",
                    max_score=10,
                ),
            ]
            session.add_all(questions)
        session.commit()
