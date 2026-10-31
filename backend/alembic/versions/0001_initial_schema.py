"""Create the initial application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_departments_slug", "departments", ["slug"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supabase_user_id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("supabase_user_id"),
    )
    op.create_index("ix_user_profiles_supabase_user_id", "user_profiles", ["supabase_user_id"], unique=False)

    op.create_table(
        "competencies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department_id", "slug", name="uq_competency_department_slug"),
    )
    op.create_index("ix_competencies_department_id", "competencies", ["department_id"], unique=False)

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_assessments_department_id", "assessments", ["department_id"], unique=False)
    op.create_index("ix_assessments_slug", "assessments", ["slug"], unique=False)

    op.create_table(
        "assessment_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assessment_id", "version_number", name="uq_assessment_version_number"),
    )
    op.create_index("ix_assessment_versions_assessment_id", "assessment_versions", ["assessment_id"], unique=False)

    op.create_table(
        "assessment_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assessment_version_id", sa.Integer(), nullable=False),
        sa.Column("competency_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("starter_code", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=40), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_version_id"], ["assessment_versions.id"]),
        sa.ForeignKeyConstraint(["competency_id"], ["competencies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assessment_questions_assessment_version_id",
        "assessment_questions",
        ["assessment_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessment_questions_competency_id",
        "assessment_questions",
        ["competency_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_questions_competency_id", table_name="assessment_questions")
    op.drop_index("ix_assessment_questions_assessment_version_id", table_name="assessment_questions")
    op.drop_table("assessment_questions")
    op.drop_index("ix_assessment_versions_assessment_id", table_name="assessment_versions")
    op.drop_table("assessment_versions")
    op.drop_index("ix_assessments_slug", table_name="assessments")
    op.drop_index("ix_assessments_department_id", table_name="assessments")
    op.drop_table("assessments")
    op.drop_index("ix_competencies_department_id", table_name="competencies")
    op.drop_table("competencies")
    op.drop_index("ix_user_profiles_supabase_user_id", table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index("ix_departments_slug", table_name="departments")
    op.drop_table("departments")
