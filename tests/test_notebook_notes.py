"""Tests for stub note creation functionality."""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub import config
from doughub.models import Base
from doughub.persistence import QuestionRepository


@pytest.fixture
def note_repo_db() -> Generator[tuple[QuestionRepository, Path], None, None]:
    """Create a temporary database and repository for note tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create database
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        # Setup notes directory
        notes_dir = Path(tmpdir) / "notes"
        original_notes_dir = config.NOTES_DIR
        config.NOTES_DIR = str(notes_dir)

        yield repo, notes_dir

        # Cleanup
        config.NOTES_DIR = original_notes_dir
        session.close()
        engine.dispose()


class TestNoteCreation:
    """Test stub note file creation."""

    def test_create_note_for_new_question(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test creating a note for a question without one."""
        repo, notes_dir = note_repo_db

        # Create a question
        source = repo.get_or_create_source("TestSource")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q001",
            "raw_html": "<p>Test question</p>",
            "raw_metadata_json": json.dumps({"title": "Test Question"}),
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Create note
        note_path_result = repo.ensure_note_for_question(question_id)

        assert note_path_result is not None
        assert Path(note_path_result).exists()
        assert Path(note_path_result).parent == notes_dir
        note_path = note_path_result

        # Verify note content
        with open(note_path, encoding="utf-8") as f:
            content = f.read()

        assert "---" in content
        assert f"question_id: {question_id}" in content
        assert "source: TestSource" in content
        assert "source_key: Q001" in content
        assert "# Notes" in content

    def test_idempotent_note_creation(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test that calling ensure_note multiple times doesn't recreate the note."""
        repo, notes_dir = note_repo_db

        # Create a question
        source = repo.get_or_create_source("TestSource")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q002",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Create note first time
        note_path_1 = repo.ensure_note_for_question(question_id)
        repo.commit()
        assert note_path_1 is not None

        # Add custom content
        with open(note_path_1, "a", encoding="utf-8") as f:
            f.write("\n\n## My Custom Notes\n\nThis should be preserved.\n")

        # Call ensure_note again
        note_path_2 = repo.ensure_note_for_question(question_id)
        repo.commit()
        assert note_path_2 is not None

        # Should return same path
        assert note_path_1 == note_path_2

        # Custom content should be preserved
        with open(note_path_2, encoding="utf-8") as f:
            content = f.read()

        assert "## My Custom Notes" in content
        assert "This should be preserved" in content

    def test_note_path_updated_in_database(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test that note_path is correctly updated in the database."""
        repo, _notes_dir = note_repo_db

        # Create a question
        source = repo.get_or_create_source("TestSource")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q003",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Initially, note_path should be None
        assert question.note_path is None

        # Create note
        note_path = repo.ensure_note_for_question(question_id)
        repo.commit()

        # Retrieve question again and verify note_path
        updated_question = repo.get_question_by_id(question_id)
        assert updated_question is not None
        assert updated_question.note_path == note_path

    def test_note_with_metadata_fields(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test that metadata fields are included in YAML frontmatter."""
        repo, _notes_dir = note_repo_db

        # Create a question with rich metadata
        source = repo.get_or_create_source("TestSource")
        metadata = {
            "title": "Complex Question",
            "category": "Cardiology",
            "difficulty": "hard",
            "tags": ["arrhythmia", "ecg"],
        }
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q004",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": json.dumps(metadata),
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Create note
        note_path = repo.ensure_note_for_question(question_id)
        assert note_path is not None

        # Check frontmatter includes metadata
        with open(note_path, encoding="utf-8") as f:
            content = f.read()

        assert "title: Complex Question" in content
        assert "category: Cardiology" in content


class TestEdgeCases:
    """Test edge cases in note creation."""

    def test_nonexistent_question(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test handling of nonexistent question ID."""
        repo, _notes_dir = note_repo_db

        # Try to create note for nonexistent question
        note_path = repo.ensure_note_for_question(99999)

        assert note_path is None

    def test_special_characters_in_filename(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test that special characters are sanitized in filenames."""
        repo, _notes_dir = note_repo_db

        # Create question with problematic characters in key
        source = repo.get_or_create_source("Test/Source")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q/005/Special",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Create note
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None
        # Verify path doesn't contain forward slashes (except directory separators)
        filename = Path(note_path).name
        assert "/" not in filename
        assert "\\" not in filename

    def test_long_question_key(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test handling of very long question keys."""
        repo, _notes_dir = note_repo_db

        # Create question with long key
        source = repo.get_or_create_source("TestSource")
        long_key = "Q" + "0" * 200  # Very long key
        question_data = {
            "source_id": source.source_id,
            "source_question_key": long_key,
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Should still create note successfully
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None
        assert Path(note_path).exists()

    def test_note_creation_recreates_deleted_directory(
        self, note_repo_db: tuple[QuestionRepository, Path]
    ) -> None:
        """Test that note creation recreates notes directory if deleted."""
        repo, notes_dir = note_repo_db

        # Create a question
        source = repo.get_or_create_source("TestSource")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q006",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Delete notes directory
        if notes_dir.exists():
            import shutil

            shutil.rmtree(notes_dir)

        assert not notes_dir.exists()

        # Create note - should recreate directory
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None
        assert notes_dir.exists()
        assert Path(note_path).exists()

    def test_yaml_frontmatter_format(self, note_repo_db: tuple[QuestionRepository, Path]) -> None:
        """Test that YAML frontmatter is properly formatted."""
        repo, _notes_dir = note_repo_db

        # Create a question
        source = repo.get_or_create_source("TestSource")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q007",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": json.dumps({"title": "Test"}),
        }
        question = repo.add_question(question_data)
        repo.commit()

        question_id = int(question.question_id)

        # Create note
        note_path = repo.ensure_note_for_question(question_id)
        assert note_path is not None

        # Parse frontmatter
        with open(note_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Should start with ---
        assert lines[0].strip() == "---"

        # Find closing ---
        closing_index = next(
            i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"
        )

        # Everything between should be valid YAML-like content
        frontmatter = lines[1:closing_index]
        assert all(":" in line or line.strip() == "" for line in frontmatter)

        # After closing ---, should have content
        assert closing_index < len(lines) - 1
