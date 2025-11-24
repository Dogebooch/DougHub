"""Tests for notebook database schema and migrations."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from doughub.models import Base
from doughub.persistence import QuestionRepository


@pytest.fixture
def temp_db() -> Generator[tuple[Engine, Path], None, None]:
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)

        yield engine, db_path

        # Cleanup
        engine.dispose()


class TestNotebookSchemaMigration:
    """Test the note_path field addition to Question model."""

    def test_note_path_field_exists(self, temp_db: tuple) -> None:
        """Test that note_path column exists in Question table."""
        engine, _db_path = temp_db

        # Inspect the schema
        inspector = inspect(engine)
        columns = inspector.get_columns("questions")
        column_names = [col["name"] for col in columns]

        assert "note_path" in column_names

    def test_note_path_is_nullable(self, temp_db: tuple) -> None:
        """Test that note_path column is nullable."""
        engine, _db_path = temp_db

        inspector = inspect(engine)
        columns = inspector.get_columns("questions")
        note_path_col = next(col for col in columns if col["name"] == "note_path")

        assert note_path_col["nullable"] is True

    def test_note_path_initial_value_is_null(self, temp_db: tuple) -> None:
        """Test that new questions have NULL note_path by default."""
        engine, _db_path = temp_db

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        try:
            # Create a source and question
            source = repo.get_or_create_source("TestSource")
            question_data = {
                "source_id": source.source_id,
                "source_question_key": "Q001",
                "raw_html": "<p>Test</p>",
                "raw_metadata_json": "{}",
            }
            question = repo.add_question(question_data)
            repo.commit()

            # Verify note_path is None
            assert question.note_path is None
        finally:
            session.close()

    def test_note_path_can_be_set_and_persisted(self, temp_db: tuple) -> None:
        """Test that note_path can be set and retrieved."""
        engine, _db_path = temp_db

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        try:
            # Create a question
            source = repo.get_or_create_source("TestSource")
            question_data = {
                "source_id": source.source_id,
                "source_question_key": "Q002",
                "raw_html": "<p>Test</p>",
                "raw_metadata_json": "{}",
            }
            _question = repo.add_question(question_data)

            # Set note_path
            test_path = "/path/to/notes/test.md"
            _question.note_path = test_path
            repo.commit()

            question_id = int(_question.question_id)
        finally:
            session.close()

        # Reopen session to verify persistence
        session2 = SessionLocal()
        repo2 = QuestionRepository(session2)
        try:
            retrieved_question = repo2.get_question_by_id(question_id)

            assert retrieved_question is not None
            assert retrieved_question.note_path == test_path
        finally:
            session2.close()

    def test_note_path_can_be_updated(self, temp_db: tuple) -> None:
        """Test that note_path can be updated to a new value."""
        engine, _db_path = temp_db

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        try:
            # Create a question with initial note_path
            source = repo.get_or_create_source("TestSource")
            question_data = {
                "source_id": source.source_id,
                "source_question_key": "Q003",
                "raw_html": "<p>Test</p>",
                "raw_metadata_json": "{}",
            }
            question = repo.add_question(question_data)
            question.note_path = "/old/path.md"
            repo.commit()

            # Update to new path
            question.note_path = "/new/path.md"
            repo.commit()

            question_id = int(question.question_id)
        finally:
            session.close()

        # Verify the update
        session2 = SessionLocal()
        repo2 = QuestionRepository(session2)
        try:
            retrieved_question = repo2.get_question_by_id(question_id)

            assert retrieved_question is not None
            assert retrieved_question.note_path == "/new/path.md"
        finally:
            session2.close()


class TestBackwardCompatibility:
    """Test that new schema works with existing data patterns."""

    def test_existing_questions_work_without_note_path(self, temp_db: tuple) -> None:
        """Test that questions created before migration still work."""
        engine, _db_path = temp_db

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        try:
            # Simulate old questions (note_path will be NULL)
            source = repo.get_or_create_source("OldSource")
            for i in range(5):
                question_data = {
                    "source_id": source.source_id,
                    "source_question_key": f"OLD_Q{i:03d}",
                    "raw_html": f"<p>Old question {i}</p>",
                    "raw_metadata_json": "{}",
                }
                repo.add_question(question_data)

            repo.commit()

            # Verify all questions can be retrieved
            questions = repo.get_all_questions()
            assert len(questions) == 5

            # All should have NULL note_path
            for question in questions:
                assert question.note_path is None
        finally:
            session.close()

    def test_mixed_questions_with_and_without_notes(self, temp_db: tuple) -> None:
        """Test queries work with mixed note_path values."""
        engine, _db_path = temp_db

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        try:
            source = repo.get_or_create_source("MixedSource")

            # Create questions with and without note_path
            for i in range(10):
                question_data = {
                    "source_id": source.source_id,
                    "source_question_key": f"MIX_Q{i:03d}",
                    "raw_html": f"<p>Question {i}</p>",
                    "raw_metadata_json": "{}",
                }
                _question = repo.add_question(question_data)

                # Set note_path for even-numbered questions
                if i % 2 == 0:
                    _question.note_path = f"/notes/question_{i}.md"

            repo.commit()

            # Retrieve and verify
            questions = repo.get_all_questions()
            assert len(questions) == 10

            questions_with_notes = [q for q in questions if q.note_path is not None]
            questions_without_notes = [q for q in questions if q.note_path is None]

            assert len(questions_with_notes) == 5
            assert len(questions_without_notes) == 5
        finally:
            session.close()


