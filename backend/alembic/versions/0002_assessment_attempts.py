"""Add candidate assessment attempts and answers.

Revision ID: 0002_assessment_attempts
Revises: 0001_initial_schema
Create Date: 2026-10-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_assessment_attempts"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_assessment_version_id_assessment",
        "assessment_versions",
        ["id", "assessment_id"],
        unique=True,
    )
    op.create_table(
        "assessment_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supabase_user_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("assessment_version_id", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name="fk_attempt_assessment",
        ),
        sa.ForeignKeyConstraint(
            ["assessment_version_id", "assessment_id"],
            ["assessment_versions.id", "assessment_versions.assessment_id"],
            name="fk_attempt_version_assessment",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "supabase_user_id",
            "assessment_id",
            "attempt_number",
            name="uq_attempt_candidate_assessment_number",
        ),
    )
    op.create_index(
        "ix_assessment_attempts_supabase_user_id",
        "assessment_attempts",
        ["supabase_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessment_attempts_assessment_id",
        "assessment_attempts",
        ["assessment_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessment_attempts_assessment_version_id",
        "assessment_attempts",
        ["assessment_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_attempt_active_candidate_assessment",
        "assessment_attempts",
        ["supabase_user_id", "assessment_id"],
        unique=True,
        sqlite_where=sa.text("status = 'in_progress'"),
    )
    op.create_table(
        "assessment_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("code_content", sa.Text(), nullable=False),
        sa.Column("code_language", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["assessment_attempts.id"],
            name="fk_answer_attempt",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["assessment_questions.id"],
            name="fk_answer_question",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", "question_id", name="uq_answer_attempt_question"),
    )
    op.create_index(
        "ix_assessment_answers_attempt_id",
        "assessment_answers",
        ["attempt_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessment_answers_question_id",
        "assessment_answers",
        ["question_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_answers_question_id", table_name="assessment_answers")
    op.drop_index("ix_assessment_answers_attempt_id", table_name="assessment_answers")
    op.drop_table("assessment_answers")
    op.drop_index("ix_attempt_active_candidate_assessment", table_name="assessment_attempts")
    op.drop_index("ix_assessment_attempts_assessment_version_id", table_name="assessment_attempts")
    op.drop_index("ix_assessment_attempts_assessment_id", table_name="assessment_attempts")
    op.drop_index("ix_assessment_attempts_supabase_user_id", table_name="assessment_attempts")
    op.drop_table("assessment_attempts")
    op.drop_index("uq_assessment_version_id_assessment", table_name="assessment_versions")
