from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assessment, AssessmentQuestion, AssessmentVersion, Competency, Department
from app.schemas import (
    AssessmentDetailResponse,
    AssessmentListItemResponse,
    AssessmentQuestionResponse,
    AssessmentVersionResponse,
    CompetencyResponse,
)

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def published_version(db: Session, assessment: Assessment) -> AssessmentVersion | None:
    return db.scalar(
        select(AssessmentVersion)
        .where(
            AssessmentVersion.assessment_id == assessment.id,
            AssessmentVersion.status == "published",
        )
        .order_by(AssessmentVersion.version_number.desc())
    )


def published_assessment_list_item(
    db: Session, assessment: Assessment, department: Department
) -> AssessmentListItemResponse | None:
    version = published_version(db, assessment)
    if version is None:
        return None
    return AssessmentListItemResponse(
        id=assessment.id,
        slug=assessment.slug,
        name=assessment.name,
        description=assessment.description,
        department_name=department.name,
        version=version.version_number,
    )


@router.get("", response_model=list[AssessmentListItemResponse])
def list_assessments(db: Session = Depends(get_db)) -> list[AssessmentListItemResponse]:
    assessments = db.scalars(
        select(Assessment)
        .where(Assessment.status == "active")
        .order_by(Assessment.created_at, Assessment.id)
    ).all()
    result: list[AssessmentListItemResponse] = []
    for assessment in assessments:
        department = db.get(Department, assessment.department_id)
        if department is None:
            continue
        item = published_assessment_list_item(db, assessment, department)
        if item is not None:
            result.append(item)
    return result


@router.get("/{assessment_slug}", response_model=AssessmentDetailResponse)
def get_assessment(
    assessment_slug: str,
    db: Session = Depends(get_db),
) -> AssessmentDetailResponse:
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.slug == assessment_slug,
            Assessment.status == "active",
        )
    )
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    version = published_version(db, assessment)
    department = db.get(Department, assessment.department_id)
    if version is None or department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    questions = db.scalars(
        select(AssessmentQuestion)
        .where(AssessmentQuestion.assessment_version_id == version.id)
        .order_by(AssessmentQuestion.position, AssessmentQuestion.id)
    ).all()
    question_responses: list[AssessmentQuestionResponse] = []
    for question in questions:
        competency = db.get(Competency, question.competency_id)
        if competency is None:
            continue
        question_responses.append(
            AssessmentQuestionResponse(
                id=question.id,
                position=question.position,
                type=question.type,
                prompt=question.prompt,
                instructions=question.instructions,
                starter_code=question.starter_code,
                language=question.language,
                max_score=question.max_score,
                competency=CompetencyResponse(
                    id=competency.id,
                    name=competency.name,
                    slug=competency.slug,
                    description=competency.description,
                ),
            )
        )
    return AssessmentDetailResponse(
        id=assessment.id,
        slug=assessment.slug,
        name=assessment.name,
        description=assessment.description,
        department_name=department.name,
        version=AssessmentVersionResponse(
            id=version.id,
            version_number=version.version_number,
            instructions=version.instructions,
            time_limit_minutes=version.time_limit_minutes,
            questions=question_responses,
        ),
    )
