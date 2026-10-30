from datetime import datetime

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
