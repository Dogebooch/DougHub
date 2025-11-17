"""Tests for metadata sync functionality (Phase 3)."""

from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.models import Base
from doughub.notebook.sync import _parse_note_frontmatter, scan_and_parse_notes
from doughub.persistence.repository import QuestionRepository


class TestFrontmatterParsing:
    """Tests for YAML frontmatter parsing."""

    def test_parse_valid_frontmatter(self, tmp_path: Path) -> None:
        """Test parsing a note file with valid YAML frontmatter."""
        note_file = tmp_path / "test_note.md"
        note_file.write_text(
            """---
question_id: 42
source: MKSAP_19
tags: ["cardiology", "urgent"]
state: review
---

# Notes

Some content here.
"""
        )

        metadata = _parse_note_frontmatter(note_file)
        assert metadata is not None
        assert metadata["question_id"] == 42
        assert metadata["source"] == "MKSAP_19"
        assert metadata["tags"] == ["cardiology", "urgent"]
        assert metadata["state"] == "review"

    def test_parse_empty_frontmatter(self, tmp_path: Path) -> None:
        """Test parsing a note file with empty frontmatter."""
        note_file = tmp_path / "test_note.md"
        note_file.write_text(
            """---

---

# Notes
"""
        )

        metadata = _parse_note_frontmatter(note_file)
        # Empty frontmatter parsed by YAML results in None, which we convert to {}
        assert metadata == {} or metadata is None

    def test_parse_no_frontmatter(self, tmp_path: Path) -> None:
        """Test parsing a note file without frontmatter."""
        note_file = tmp_path / "test_note.md"
        note_file.write_text("# Just a heading\n\nSome content.")

        metadata = _parse_note_frontmatter(note_file)
        assert metadata is None

    def test_parse_malformed_yaml(self, tmp_path: Path) -> None:
        """Test parsing a note file with malformed YAML."""
        note_file = tmp_path / "test_note.md"
        note_file.write_text(
            """---
question_id: 42
unclosed_string: "this is bad
---

# Notes
"""
        )

        # Should raise a YAML parsing error (yaml.YAMLError and subclasses)
        # Our implementation logs and re-raises these errors
        with pytest.raises(Exception):  # noqa: B017
            _parse_note_frontmatter(note_file)


class TestScanAndParseNotes:
    """Tests for directory scanning and parsing."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning an empty directory."""
        notes = list(scan_and_parse_notes(tmp_path))
        assert notes == []

    def test_scan_directory_with_valid_notes(self, tmp_path: Path) -> None:
        """Test scanning a directory with valid note files."""
        # Create two valid note files
        (tmp_path / "note1.md").write_text(
            """---
question_id: 1
tags: ["tag1"]
---
Content
"""
        )
        (tmp_path / "note2.md").write_text(
            """---
question_id: 2
state: pending
---
Content
"""
        )

        notes = list(scan_and_parse_notes(tmp_path))
        assert len(notes) == 2
        assert notes[0]["question_id"] == 1
        assert notes[1]["question_id"] == 2

    def test_scan_skips_notes_without_question_id(self, tmp_path: Path) -> None:
        """Test that notes without question_id are skipped."""
        (tmp_path / "invalid.md").write_text(
            """---
title: Some note
---
Content
"""
        )

        notes = list(scan_and_parse_notes(tmp_path))
        assert notes == []

    def test_scan_handles_malformed_notes(self, tmp_path: Path) -> None:
        """Test that malformed notes are logged but don't stop iteration."""
        (tmp_path / "good.md").write_text(
            """---
question_id: 1
---
Content
"""
        )
        (tmp_path / "bad.md").write_text(
            """---
question_id: 2
bad_yaml: "unclosed
---
Content
"""
        )
        (tmp_path / "good2.md").write_text(
            """---
question_id: 3
---
Content
"""
        )

        # Should get the two good notes despite the bad one
        notes = list(scan_and_parse_notes(tmp_path))
        assert len(notes) == 2
        assert {n["question_id"] for n in notes} == {1, 3}

    def test_scan_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test scanning a directory that doesn't exist."""
        nonexistent = tmp_path / "nonexistent"
        notes = list(scan_and_parse_notes(nonexistent))
        assert notes == []


class TestRepositoryMetadataUpdate:
    """Tests for repository update_question_from_metadata method."""

    @pytest.fixture
    def db_session(self):  # type: ignore[no-untyped-def]
        """Create an in-memory SQLite session for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    @pytest.fixture
    def repository(self, db_session) -> QuestionRepository:  # type: ignore[no-untyped-def]
        """Create a QuestionRepository instance."""
        return QuestionRepository(db_session)

    def test_update_question_from_metadata_tags(
        self, repository: QuestionRepository
    ) -> None:
        """Test updating question tags from metadata."""
        # Create a source and question
        source = repository.get_or_create_source("MKSAP_19")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q1",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repository.add_question(question_data)
        repository.commit()

        # Update with metadata
        metadata = {
            "question_id": question.question_id,
            "tags": ["cardiology", "urgent"],
        }
        result = repository.update_question_from_metadata(metadata)
        repository.commit()

        assert result is True
        updated = repository.get_question_by_id(question.question_id)
        assert updated is not None
        assert updated.tags == '["cardiology", "urgent"]'

    def test_update_question_from_metadata_state(
        self, repository: QuestionRepository
    ) -> None:
        """Test updating question state from metadata."""
        # Create a source and question
        source = repository.get_or_create_source("MKSAP_19")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "Q1",
            "raw_html": "<p>Test</p>",
            "raw_metadata_json": "{}",
        }
        question = repository.add_question(question_data)
        repository.commit()

        # Update with metadata
        metadata = {
            "question_id": question.question_id,
            "state": "review",
        }
        result = repository.update_question_from_metadata(metadata)
        repository.commit()

        assert result is True
        updated = repository.get_question_by_id(question.question_id)
        assert updated is not None
        assert updated.state == "review"

    def test_update_nonexistent_question(self, repository: QuestionRepository) -> None:
        """Test updating a nonexistent question returns False."""
        metadata = {
            "question_id": 99999,
            "tags": ["test"],
        }
        result = repository.update_question_from_metadata(metadata)
        assert result is False

    def test_update_without_question_id(self, repository: QuestionRepository) -> None:
        """Test updating without question_id returns False."""
        metadata = {
            "tags": ["test"],
        }
        result = repository.update_question_from_metadata(metadata)
        assert result is False
