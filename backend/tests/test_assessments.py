import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.models import Assessment, AssessmentQuestion, AssessmentVersion, Competency, Department
from app.routers.assessments import get_assessment, list_assessments


class AssessmentDefinitionTests(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        self.engine = engine
        self.session = sessionmaker(bind=engine)()
        from app.database import Base

        Base.metadata.create_all(engine)
        department = Department(
            name="Frontend Engineering",
            slug="frontend-engineering",
            description="Frontend work.",
            status="active",
        )
        self.session.add(department)
        self.session.flush()
        competency = Competency(
            department_id=department.id,
            name="React and TypeScript",
            slug="react-typescript",
            description="Build typed React components.",
        )
        self.session.add(competency)
        self.session.flush()
        assessment = Assessment(
            department_id=department.id,
            name="Frontend Engineering Foundations",
            slug="frontend-engineering-foundations",
            description="A practical frontend assessment.",
            status="active",
        )
        self.session.add(assessment)
        self.session.flush()
        version = AssessmentVersion(
            assessment_id=assessment.id,
            version_number=1,
            status="published",
            instructions="Complete the practical tasks.",
            published_at=datetime.now(timezone.utc),
        )
        self.session.add(version)
        self.session.flush()
        self.session.add(
            AssessmentQuestion(
                assessment_version_id=version.id,
                competency_id=competency.id,
                position=1,
                type="coding",
                prompt="Build a typed component.",
                language="tsx",
                max_score=10,
            )
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_only_published_versions_are_discoverable(self) -> None:
        assessment = self.session.scalar(select(Assessment))
        self.session.add(
            AssessmentVersion(
                assessment_id=assessment.id,
                version_number=2,
                status="draft",
                instructions="Internal draft.",
            )
        )
        self.session.commit()

        assessments = list_assessments(self.session)

        self.assertEqual(len(assessments), 1)
        self.assertEqual(assessments[0].version, 1)

    def test_detail_includes_questions_and_competency_but_no_evaluation_fields(self) -> None:
        detail = get_assessment("frontend-engineering-foundations", self.session)

        self.assertEqual(detail.version.version_number, 1)
        self.assertEqual(len(detail.version.questions), 1)
        self.assertEqual(detail.version.questions[0].competency.slug, "react-typescript")
        self.assertFalse(hasattr(detail.version.questions[0], "score"))

    def test_missing_assessment_is_not_exposed(self) -> None:
        with self.assertRaises(Exception):
            get_assessment("does-not-exist", self.session)

    def test_assessment_seed_has_single_version_per_number(self) -> None:
        count = self.session.scalar(select(func.count()).select_from(AssessmentVersion))
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
