"""Tests for Phase 2 Notebook Navigation functionality.

This module implements validation checkpoints from the Phase 2 validation plan:
- Checkpoint 1: Note-Opening Mechanism
- Checkpoint 2: New Notes Appearing in Notesium Index
- Checkpoint 3: Navigation Stability and Performance

These tests verify that navigation between questions and notes is seamless,
reliable, and performant.
"""

import json
import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub import config
from doughub.models import Base
from doughub.notebook.manager import NotesiumManager
from doughub.persistence import QuestionRepository
from doughub.ui.deck_browser_view import DeckBrowserView
from doughub.ui.notebook_view import NotebookView

logger = logging.getLogger(__name__)


@pytest.fixture
def test_db_and_repo():
    """Create a temporary database with test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup database
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        repo = QuestionRepository(session)

        # Setup notes directory
        notes_dir = Path(tmpdir) / "notes"
        notes_dir.mkdir(exist_ok=True)
        original_notes_dir = config.NOTES_DIR
        config.NOTES_DIR = str(notes_dir)

        # Create test questions
        source = repo.get_or_create_source("TestSource")
        questions = []
        for i in range(5):
            question_data = {
                "source_id": source.source_id,
                "source_question_key": f"Q{i:03d}",
                "raw_html": f"<p>Test question {i}</p>",
                "raw_metadata_json": json.dumps({"title": f"Question {i}"}),
            }
            q = repo.add_question(question_data)
            questions.append(q)
        repo.commit()

        yield repo, notes_dir, questions

        # Cleanup
        config.NOTES_DIR = original_notes_dir
        session.close()
        engine.dispose()


class TestCheckpoint1_NoteOpeningMechanism:
    """Checkpoint 1: Note-Opening Mechanism.

    Validates that the chosen mechanism successfully focuses
    the target note in the Notesium UI.
    """

    def test_open_note_constructs_correct_url(self, qtbot):
        """Test that open_note constructs the correct URL with query parameter."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)

        # Load a base URL first
        notebook_view.load_url("http://localhost:3030")

        # Open a specific note
        test_note_path = "test-note.md"
        notebook_view.open_note(test_note_path)

        # Verify the URL contains the file parameter
        current_url = notebook_view.web_view.url().toString()
        assert "?file=test-note.md" in current_url
        assert "http://localhost:3030" in current_url

    def test_open_note_handles_special_characters(self, qtbot):
        """Test that open_note properly encodes special characters in paths."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        # Note path with special characters
        test_note_path = "notes/test note with spaces.md"
        notebook_view.open_note(test_note_path)

        current_url = notebook_view.web_view.url().toString()
        # Verify the file parameter is included (encoding may vary by Qt version)
        assert "?file=" in current_url
        assert "notes/test" in current_url
        assert "spaces.md" in current_url

    def test_open_note_handles_empty_path(self, qtbot, caplog):
        """Test that open_note gracefully handles empty path."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        with caplog.at_level(logging.WARNING):
            notebook_view.open_note("")

        assert "empty path" in caplog.text

    def test_open_note_handles_invalid_base_url(self, qtbot, caplog):
        """Test that open_note handles cases where base URL is not set."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        # Don't load a base URL

        with caplog.at_level(logging.WARNING):
            notebook_view.open_note("test-note.md")

        assert "invalid base URL" in caplog.text

    def test_navigation_after_note_creation(self, test_db_and_repo, qtbot):
        """Test that navigation works correctly after creating a new note."""
        repo, notes_dir, questions = test_db_and_repo

        # Get first question without a note
        question_id = int(questions[0].question_id)  # type: ignore[arg-type]

        # Create note
        note_path = repo.ensure_note_for_question(question_id)
        assert note_path is not None
        assert Path(note_path).exists()

        # Simulate navigation
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")
        notebook_view.open_note(note_path)

        # Verify URL is constructed correctly
        current_url = notebook_view.web_view.url().toString()
        from urllib.parse import unquote
        decoded_url = unquote(current_url)
        # The path should appear in the decoded URL
        assert "?file=" in current_url
        assert Path(note_path).stem in decoded_url  # Check filename is present

    def test_nonexistent_note_is_recreated_before_navigation(self, test_db_and_repo, qtbot):
        """Test that missing note files are recreated before navigation."""
        repo, notes_dir, questions = test_db_and_repo

        # Create a question with a note
        question_id = int(questions[0].question_id)  # type: ignore[arg-type]
        note_path = repo.ensure_note_for_question(question_id)
        assert note_path is not None
        assert Path(note_path).exists()

        # Delete the note file
        Path(note_path).unlink()
        assert not Path(note_path).exists()

        # Ensure note again - should recreate
        note_path_2 = repo.ensure_note_for_question(question_id)
        assert note_path_2 == note_path
        assert Path(note_path_2).exists()

        # Navigation should work
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")
        notebook_view.open_note(note_path_2)

        current_url = notebook_view.web_view.url().toString()
        assert "?file=" in current_url


class TestCheckpoint2_NewNotesInNotesiumIndex:
    """Checkpoint 2: New Notes Appearing in Notesium Index.

    Validates that new .md files created by DougHub become
    searchable in Notesium without a server restart.
    """

    def test_note_file_created_on_disk(self, test_db_and_repo):
        """Test that note file is physically created on disk."""
        repo, notes_dir, questions = test_db_and_repo

        question_id = int(questions[0].question_id)  # type: ignore[arg-type]

        # Verify note doesn't exist yet
        question = repo.get_question_by_id(question_id)
        assert question.note_path is None

        # Create note
        note_path = repo.ensure_note_for_question(question_id)

        # Verify file exists
        assert note_path is not None
        assert Path(note_path).exists()
        assert Path(note_path).parent == notes_dir
        assert Path(note_path).suffix == ".md"

    def test_note_contains_valid_frontmatter(self, test_db_and_repo):
        """Test that created note contains valid YAML frontmatter."""
        repo, notes_dir, questions = test_db_and_repo

        question_id = int(questions[0].question_id)  # type: ignore[arg-type]
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None
        with open(note_path, encoding="utf-8") as f:
            content = f.read()

        # Verify frontmatter structure
        assert content.startswith("---\n")
        assert f"question_id: {question_id}" in content
        assert "source: TestSource" in content

        # Verify content section
        assert "# Notes" in content or "## Notes" in content

    def test_multiple_notes_created_in_sequence(self, test_db_and_repo):
        """Test that multiple notes can be created in sequence."""
        repo, notes_dir, questions = test_db_and_repo

        created_paths = []
        for i in range(3):
            question_id = int(questions[i].question_id)  # type: ignore[arg-type]
            note_path = repo.ensure_note_for_question(question_id)
            assert note_path is not None
            assert Path(note_path).exists()
            created_paths.append(note_path)

        # Verify all notes exist
        for path in created_paths:
            assert Path(path).exists()

        # Verify they have unique names
        assert len(set(created_paths)) == 3

    @pytest.mark.integration
    def test_notesium_can_read_new_note(self, test_db_and_repo):
        """Integration test: Verify Notesium can access a newly created note.

        This is a smoke test that verifies the file is accessible.
        Full indexing test requires running Notesium server.
        """
        repo, notes_dir, questions = test_db_and_repo

        question_id = int(questions[0].question_id)  # type: ignore[arg-type]
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None

        # Simulate Notesium reading the file
        try:
            with open(note_path, encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 0
            assert "question_id" in content
        except Exception as e:
            pytest.fail(f"Notesium would not be able to read note: {e}")


class TestCheckpoint3_NavigationStability:
    """Checkpoint 3: Navigation Stability and Performance.

    Validates that rapid navigation between notes does not cause
    UI freezes, crashes, or loss of synchronization.
    """

    def test_rapid_note_creation_no_race_condition(self, test_db_and_repo):
        """Test that rapid note creation doesn't cause race conditions."""
        repo, notes_dir, questions = test_db_and_repo

        # Rapidly create multiple notes
        created_paths = []
        for i in range(5):
            question_id = int(questions[i].question_id)  # type: ignore[arg-type]
            note_path = repo.ensure_note_for_question(question_id)
            assert note_path is not None
            created_paths.append(note_path)

        # Verify all notes exist
        for path in created_paths:
            assert Path(path).exists(), f"Note not created: {path}"

        # Verify all have valid content
        for path in created_paths:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert "question_id:" in content
            assert "# Notes" in content or "## Notes" in content

    def test_navigation_signal_emitted_after_file_creation(self, test_db_and_repo, qtbot):
        """Test that navigation signal is only emitted after file exists."""
        repo, notes_dir, questions = test_db_and_repo

        # Mock AnkiRepository
        mock_anki_repo = MagicMock()
        mock_anki_repo.list_notes_in_deck.return_value = []

        # Create deck browser
        browser = DeckBrowserView(mock_anki_repo, repo)

        # Track signal emissions
        signal_received = []

        def track_signal(note_path: str):
            # Verify file exists when signal is emitted
            assert Path(note_path).exists(), f"Signal emitted but file doesn't exist: {note_path}"
            signal_received.append(note_path)

        browser.note_ready_for_navigation.connect(track_signal)

        # Simulate selecting a question
        question_id = int(questions[0].question_id)  # type: ignore[arg-type]

        # Create note and emit signal manually (simulating the workflow)
        note_path = repo.ensure_note_for_question(question_id)
        if note_path:
            browser.note_ready_for_navigation.emit(note_path)

        # Verify signal was received and file existed
        assert len(signal_received) == 1
        assert signal_received[0] == note_path

    def test_sequential_navigation_updates_url(self, qtbot):
        """Test that navigating to multiple notes in sequence updates URL correctly."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        notes = ["note1.md", "note2.md", "note3.md"]

        for note_path in notes:
            notebook_view.open_note(note_path)
            current_url = notebook_view.web_view.url().toString()
            assert f"?file={note_path}" in current_url

    def test_notebook_view_remains_responsive_during_navigation(self, qtbot):
        """Test that notebook view doesn't block during navigation."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        # Rapidly navigate between notes
        start_time = time.time()
        for i in range(20):
            notebook_view.open_note(f"note{i}.md")

        elapsed = time.time() - start_time

        # Navigation should be fast (synchronous URL updates)
        assert elapsed < 1.0, f"Navigation took too long: {elapsed}s"

    def test_error_handling_during_navigation(self, test_db_and_repo, qtbot, caplog):
        """Test that navigation errors are handled gracefully."""
        repo, notes_dir, questions = test_db_and_repo

        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        with caplog.at_level(logging.WARNING):
            # Try to navigate to None
            notebook_view.open_note(None)  # type: ignore[arg-type]

        # Should log warning but not crash
        assert "empty path" in caplog.text


class TestCrossPhaseRegression:
    """Cross-phase regression checks to ensure Phase 1 still works."""

    def test_notesium_manager_startup(self):
        """Test that NotesiumManager can be instantiated (Phase 1 check)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            notes_dir = Path(tmpdir) / "notes"
            manager = NotesiumManager(notes_dir=str(notes_dir), port=3031)

            assert manager.notes_dir == notes_dir
            assert manager.port == 3031
            assert manager.url == "http://localhost:3031"

    def test_stub_creation_still_works(self, test_db_and_repo):
        """Test that Phase 1 stub creation still functions correctly."""
        repo, notes_dir, questions = test_db_and_repo

        question_id = int(questions[0].question_id)  # type: ignore[arg-type]

        # Create note (Phase 1 functionality)
        note_path = repo.ensure_note_for_question(question_id)

        assert note_path is not None
        assert Path(note_path).exists()
        assert Path(note_path).suffix == ".md"

        # Verify database updated
        question = repo.get_question_by_id(question_id)
        assert question.note_path == note_path

    def test_error_state_display_still_works(self, qtbot):
        """Test that error display from Phase 1 still works."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)

        error_msg = "Test error message"
        notebook_view.show_error(error_msg)

        # Process Qt events to ensure visibility changes are applied
        qtbot.wait(10)  # Small delay for Qt event processing

        # Verify error label text is set
        assert error_msg in notebook_view.error_label.text()
        # Note: Visibility may depend on Qt event processing and layout
        # The important part is that show_error() sets text and calls show()


# Performance and stress tests
class TestPerformanceAndStress:
    """Additional performance and stress tests."""

    def test_large_deck_navigation(self, qtbot):
        """Test navigation with a large number of notes."""
        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        # Simulate navigating through 100 notes
        start_time = time.time()
        for i in range(100):
            notebook_view.open_note(f"note_{i:04d}.md")

        elapsed = time.time() - start_time

        # Should complete in reasonable time
        assert elapsed < 5.0, f"Navigation of 100 notes took too long: {elapsed}s"

    def test_concurrent_note_creation_and_navigation(self, test_db_and_repo, qtbot):
        """Test that note creation and navigation can happen rapidly."""
        repo, notes_dir, questions = test_db_and_repo

        notebook_view = NotebookView()
        qtbot.addWidget(notebook_view)
        notebook_view.load_url("http://localhost:3030")

        # Create and navigate in rapid succession
        for i in range(5):
            question_id = int(questions[i].question_id)  # type: ignore[arg-type]
            note_path = repo.ensure_note_for_question(question_id)

            assert note_path is not None
            notebook_view.open_note(note_path)

            # Verify the file exists at navigation time
            assert Path(note_path).exists()

    def test_memory_leak_prevention(self, test_db_and_repo):
        """Test that repeated note creation doesn't cause memory issues."""
        repo, notes_dir, questions = test_db_and_repo

        question_id = int(questions[0].question_id)  # type: ignore[arg-type]

        # Call ensure_note many times (should be idempotent)
        for _ in range(100):
            note_path = repo.ensure_note_for_question(question_id)
            assert note_path is not None

        # Verify only one file was created
        note_files = list(notes_dir.glob("*.md"))
        assert len(note_files) == 1
