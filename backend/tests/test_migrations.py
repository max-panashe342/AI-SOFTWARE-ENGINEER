import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC = [sys.executable, "-m", "alembic"]
TABLES = (
    "departments",
    "user_profiles",
    "competencies",
    "assessments",
    "assessment_versions",
    "assessment_questions",
)
PHASE_1_TABLES = ("assessment_attempts", "assessment_answers")


def run_command(arguments: list[str], database_path: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["AI_ERA_DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    return subprocess.run(
        arguments,
        cwd=BACKEND_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def database_snapshot(database_path: Path) -> dict[str, object]:
    connection = sqlite3.connect(database_path)
    snapshot: dict[str, object] = {}
    for table in TABLES:
        table_sql = connection.execute(
            "select sql from sqlite_master where type='table' and name=?",
            (table,),
        ).fetchone()[0]
        indexes = []
        for index in connection.execute(f"pragma index_list({table})").fetchall():
            index_name = index[1]
            indexes.append(
                {
                    "name": index_name,
                    "unique": index[2],
                    "origin": index[3],
                    "partial": index[4],
                    "sql": connection.execute(
                        "select sql from sqlite_master where type='index' and name=?",
                        (index_name,),
                    ).fetchone()[0],
                    "columns": connection.execute(f"pragma index_info({index_name})").fetchall(),
                }
            )
        snapshot[table] = {
            "columns": connection.execute(f"pragma table_info({table})").fetchall(),
            "foreign_keys": connection.execute(f"pragma foreign_key_list({table})").fetchall(),
            "indexes": indexes,
            "unique_constraints": [
                index for index in indexes if index["unique"] or index["origin"] == "u"
            ],
            "table_sql": table_sql,
            "check_constraints": re.findall(r"CHECK\s*\(([^()]*)\)", table_sql, flags=re.IGNORECASE),
            "count": connection.execute(f"select count(*) from {table}").fetchone()[0],
            "ids": connection.execute(f"select id from {table} order by id").fetchall(),
        }
    connection.close()
    return snapshot


class MigrationTests(unittest.TestCase):
    def test_fresh_upgrade_seed_idempotency_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "fresh.db"

            run_command(ALEMBIC + ["upgrade", "head"], database_path)
            run_command([sys.executable, "-m", "app.seed"], database_path)
            run_command([sys.executable, "-m", "app.seed"], database_path)
            status = run_command(ALEMBIC + ["current"], database_path)

            connection = sqlite3.connect(database_path)
            tables = {
                row[0]
                for row in connection.execute("select name from sqlite_master where type='table'")
            }
            counts = {
                table: connection.execute(f"select count(*) from {table}").fetchone()[0]
                for table in TABLES
            }
            version = connection.execute("select version_num from alembic_version").fetchall()
            connection.close()

            self.assertTrue(set(TABLES).issubset(tables))
            self.assertEqual(counts["departments"], 1)
            self.assertEqual(counts["competencies"], 3)
            self.assertEqual(counts["assessments"], 1)
            self.assertEqual(counts["assessment_versions"], 1)
            self.assertEqual(counts["assessment_questions"], 3)
            self.assertEqual(counts["user_profiles"], 0)
            self.assertEqual(version, [("0002_assessment_attempts",)])
            self.assertIn("0002_assessment_attempts", status.stdout)

    def test_baseline_generated_schema_can_be_stamped_without_data_or_structure_changes(self) -> None:
        """This is a synthetic adoption test; historical adoption was verified separately on a copy."""
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "adoption.db"

            run_command(ALEMBIC + ["upgrade", "0001_initial_schema"], database_path)
            run_command([sys.executable, "-m", "app.seed"], database_path)
            connection = sqlite3.connect(database_path)
            connection.execute("drop table alembic_version")
            connection.commit()
            connection.close()

            before = database_snapshot(database_path)
            run_command(ALEMBIC + ["stamp", "0001_initial_schema"], database_path)
            after = database_snapshot(database_path)

            connection = sqlite3.connect(database_path)
            version = connection.execute("select version_num from alembic_version").fetchall()
            connection.close()

            self.assertEqual(before, after)
            self.assertEqual(version, [("0001_initial_schema",)])

    def test_application_sqlite_connections_enforce_foreign_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "application-connection.db"
            run_command(ALEMBIC + ["upgrade", "head"], database_path)
            script = """
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal, engine
from app.models import Assessment

with engine.connect() as connection:
    assert connection.scalar(text("PRAGMA foreign_keys")) == 1
    assert connection.scalar(text("PRAGMA busy_timeout")) == 5000

with SessionLocal() as session:
    session.add(Assessment(
        department_id=999999,
        slug="invalid-foreign-key-test",
        name="Invalid foreign key test",
        description="This row must not persist.",
        status="active",
    ))
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    else:
        raise AssertionError("SQLite accepted an invalid department foreign key")
"""
            run_command([sys.executable, "-c", script], database_path)

    def test_baseline_downgrade_and_upgrade_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "round-trip.db"

            run_command(ALEMBIC + ["upgrade", "head"], database_path)
            run_command(ALEMBIC + ["downgrade", "base"], database_path)
            run_command(ALEMBIC + ["upgrade", "head"], database_path)

            connection = sqlite3.connect(database_path)
            tables = {
                row[0]
                for row in connection.execute("select name from sqlite_master where type='table'")
            }
            version = connection.execute("select version_num from alembic_version").fetchall()
            connection.close()

            self.assertTrue(set(TABLES).issubset(tables))
            self.assertEqual(version, [("0002_assessment_attempts",)])

    def test_attempt_schema_preserves_baseline_and_enforces_constraints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "attempts.db"

            run_command(ALEMBIC + ["upgrade", "0001_initial_schema"], database_path)
            run_command([sys.executable, "-m", "app.seed"], database_path)

            connection = sqlite3.connect(database_path)
            connection.execute("PRAGMA foreign_keys=ON")
            baseline = {
                table: {
                    "count": connection.execute(f"select count(*) from {table}").fetchone()[0],
                    "ids": connection.execute(f"select id from {table} order by id").fetchall(),
                }
                for table in TABLES
            }
            connection.execute(
                """
                insert into departments (id, name, slug, description, status, created_at)
                values (2, 'Second Department', 'second-department', 'Second', 'active', CURRENT_TIMESTAMP)
                """
            )
            connection.execute(
                """
                insert into assessments
                    (id, department_id, slug, name, description, status, created_at)
                values
                    (2, 2, 'second-assessment', 'Second Assessment', 'Second', 'active', CURRENT_TIMESTAMP)
                """
            )
            connection.commit()
            connection.close()

            run_command(ALEMBIC + ["upgrade", "head"], database_path)

            connection = sqlite3.connect(database_path)
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute(
                """
                insert into assessment_attempts
                    (id, supabase_user_id, assessment_id, assessment_version_id,
                     attempt_number, status, started_at, created_at, updated_at)
                values
                    (1, '11111111-1111-1111-1111-111111111111', 1, 1,
                     1, 'in_progress', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
            connection.commit()

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    insert into assessment_attempts
                        (id, supabase_user_id, assessment_id, assessment_version_id,
                         attempt_number, status, started_at, created_at, updated_at)
                    values
                        (2, '22222222-2222-2222-2222-222222222222', 2, 1,
                         1, 'in_progress', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                )
            connection.rollback()

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    insert into assessment_attempts
                        (id, supabase_user_id, assessment_id, assessment_version_id,
                         attempt_number, status, started_at, created_at, updated_at)
                    values
                        (2, '11111111-1111-1111-1111-111111111111', 1, 1,
                         2, 'in_progress', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                )
            connection.rollback()

            connection.execute(
                """
                insert into assessment_attempts
                    (id, supabase_user_id, assessment_id, assessment_version_id,
                     attempt_number, status, started_at, created_at, updated_at)
                values
                    (3, '11111111-1111-1111-1111-111111111111', 1, 1,
                     2, 'submitted', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
            connection.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    insert into assessment_attempts
                        (id, supabase_user_id, assessment_id, assessment_version_id,
                         attempt_number, status, started_at, created_at, updated_at)
                    values
                        (4, '11111111-1111-1111-1111-111111111111', 1, 1,
                         2, 'submitted', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                )
            connection.rollback()
            connection.execute(
                """
                insert into assessment_answers
                    (id, attempt_id, question_id, answer_text, code_content,
                     code_language, created_at, updated_at)
                values
                    (1, 3, 1, NULL, 'const answer = true;', 'tsx',
                     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
            connection.commit()

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    insert into assessment_answers
                        (id, attempt_id, question_id, answer_text, code_content,
                         code_language, created_at, updated_at)
                    values
                        (2, 3, 1, NULL, 'const duplicate = true;', 'tsx',
                         CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                )
            connection.rollback()

            for table, expected in baseline.items():
                self.assertEqual(
                    connection.execute(f"select count(*) from {table}").fetchone()[0],
                    expected["count"] + (1 if table == "departments" else 1 if table == "assessments" else 0),
                )
                if table not in ("departments", "assessments"):
                    self.assertEqual(
                        connection.execute(f"select id from {table} order by id").fetchall(),
                        expected["ids"],
                    )

            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            connection.close()

            run_command(ALEMBIC + ["downgrade", "0001_initial_schema"], database_path)

            connection = sqlite3.connect(database_path)
            remaining_tables = {
                row[0]
                for row in connection.execute("select name from sqlite_master where type='table'")
            }
            self.assertTrue(set(TABLES).issubset(remaining_tables))
            self.assertFalse(set(PHASE_1_TABLES) & remaining_tables)
            self.assertEqual(
                connection.execute("select version_num from alembic_version").fetchall(),
                [("0001_initial_schema",)],
            )
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            connection.close()


if __name__ == "__main__":
    unittest.main()
