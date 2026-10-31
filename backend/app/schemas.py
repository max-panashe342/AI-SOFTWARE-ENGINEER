from datetime import datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str
    status: str
    created_at: datetime


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("display_name cannot be empty.")
        return normalized


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None
    display_name: str | None
    created_at: datetime
    updated_at: datetime


class CompetencyResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str


class AssessmentListItemResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    department_name: str
    version: int


class AssessmentQuestionResponse(BaseModel):
    id: int
    position: int
    type: str
    prompt: str
    instructions: str | None
    starter_code: str | None
    language: str | None
    max_score: int
    competency: CompetencyResponse


class AssessmentVersionResponse(BaseModel):
    id: int
    version_number: int
    instructions: str
    time_limit_minutes: int | None
    questions: list[AssessmentQuestionResponse]


class AssessmentDetailResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    department_name: str
    version: AssessmentVersionResponse


class StartAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssessmentAnswerUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code_content: str = Field(..., max_length=200_000)
    code_language: str = Field(..., max_length=40)
    answer_text: str | None = Field(default=None, max_length=20_000)

    @field_validator("code_content")
    @classmethod
    def validate_code_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code_content cannot be empty.")
        return value

    @field_validator("code_language")
    @classmethod
    def normalize_code_language(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("code_language cannot be empty.")
        return normalized

    @field_validator("answer_text")
    @classmethod
    def normalize_answer_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class SubmitAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AttemptSummaryResponse(BaseModel):
    id: int
    assessment_id: int
    assessment_slug: str
    assessment_name: str
    assessment_version_id: int
    version_number: int
    attempt_number: int
    status: str
    started_at: datetime
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None
    answered_count: int
    question_count: int
    is_complete: bool


class StartAttemptResponse(BaseModel):
    attempt: AttemptSummaryResponse
    created: bool


class AttemptListResponse(BaseModel):
    items: list[AttemptSummaryResponse]
    limit: int
    offset: int
    total: int


class AssessmentAnswerResponse(BaseModel):
    attempt_id: int
    question_id: int
    answer_text: str | None
    code_content: str
    code_language: str
    created_at: datetime
    updated_at: datetime


class AssessmentAnswerSaveResponse(BaseModel):
    answer: AssessmentAnswerResponse
    attempt_status: str
    answered_count: int
    question_count: int
    is_complete: bool


class AssessmentAttemptQuestionResponse(BaseModel):
    id: int
    position: int
    type: str
    prompt: str
    instructions: str | None
    starter_code: str | None
    language: str | None
    answer: AssessmentAnswerResponse | None


class AssessmentAttemptDetailResponse(AttemptSummaryResponse):
    instructions: str
    time_limit_minutes: int | None
    questions: list[AssessmentAttemptQuestionResponse]


class SubmitAttemptResponse(BaseModel):
    attempt: AttemptSummaryResponse


AttemptListLimit = Annotated[int, Query(default=20, ge=1, le=100)]
AttemptListOffset = Annotated[int, Query(default=0, ge=0)]
