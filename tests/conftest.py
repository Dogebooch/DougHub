"""Shared pytest fixtures and configuration for DougHub tests."""

import json
import logging
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from doughub.anki_client import AnkiRepository
from doughub.models import Base
from doughub.utils.anki_process import AnkiProcessManager

# Backward compatibility alias
AnkiConnectClient = AnkiRepository

logger = logging.getLogger(__name__)

# Track note IDs created during tests for cleanup
_created_note_ids: list[int] = []


@pytest.fixture(scope="session")
def anki_manager() -> Generator[AnkiProcessManager, None, None]:
    """Fixture to manage Anki process for integration tests.

    This fixture will attempt to launch Anki if it's not already running.
    It does not stop Anki after tests to avoid disrupting user workflow.
    """
    manager = AnkiProcessManager()
    if not manager.is_ankiconnect_running():
        success = manager.launch_anki(timeout=15.0)
        if not success:
            pytest.skip("Anki could not be started and is not running")
    yield manager
    # Note: We don't stop Anki after tests to avoid disrupting user's workflow


@pytest.fixture(scope="session")
def test_deck_manager(anki_manager: AnkiProcessManager) -> Generator[str, None, None]:
    """Fixture to ensure test deck exists and is available.

    Creates a dedicated test deck if it doesn't exist. The deck persists
    after tests to enable manual inspection of test data.

    Returns:
        The name of the test deck.
    """
    deck_name = "DougHub_Testing"
    client = AnkiConnectClient()

    try:
        deck_names = client.get_deck_names()
        if deck_name not in deck_names:
            logger.info(f"Creating test deck: {deck_name}")
            # AnkiConnect doesn't have createDeck, so we'll create a note in the deck
            # which will auto-create it. Then we can delete the note.
            try:
                temp_note_id = client.add_note(
                    deck_name=deck_name,
                    model_name="Basic",
                    fields={"Front": "__temp__", "Back": "__temp__"},
                    tags=["__temp__"],
                )
                # Note: We keep the note for now as a deck anchor
                # In future, implement deck creation via AnkiConnect if available
                logger.debug(f"Created temporary note {temp_note_id} to establish deck")
            except Exception as e:
                logger.warning(f"Could not create test deck: {e}")
    except Exception as e:
        logger.warning(f"Could not verify test deck: {e}")

    yield deck_name

    # Cleanup: optionally remove test deck
    # For now, we keep it to allow manual inspection
    client.close()


@pytest.fixture
def integration_client(
    anki_manager: AnkiProcessManager,
) -> Generator[AnkiRepository, None, None]:
    """Fixture to create an AnkiConnect client for integration tests.

    Skips tests if AnkiConnect is not accessible.
    """
    client = AnkiRepository()
    if not client.check_connection():
        pytest.skip("AnkiConnect is not accessible")
    yield client
    client.close()


@pytest.fixture(autouse=True, scope="function")
def track_test_notes() -> Generator[None, None, None]:
    """Autouse fixture to track and cleanup notes created during tests.

    Tests can call register_note_for_cleanup(note_id) to mark notes
    for deletion after the test completes.
    """
    global _created_note_ids
    _created_note_ids = []
    yield
    # Cleanup created notes
    if _created_note_ids:
        try:
            client = AnkiRepository()
            # Access transport directly for deleteNotes (not in public API)
            client.transport.invoke("deleteNotes", {"notes": _created_note_ids})
            logger.info(f"Cleaned up {len(_created_note_ids)} test notes")
            client.close()
        except Exception as e:
            logger.warning(f"Could not cleanup test notes: {e}")


def register_note_for_cleanup(note_id: int) -> None:
    """Register a note ID to be deleted after the current test.

    Args:
        note_id: The note ID to clean up.
    """
    global _created_note_ids
    _created_note_ids.append(note_id)


def assert_valid_note_structure(note_dict: dict[str, Any]) -> None:
    """Assert that a note dictionary has the expected structure.

    Args:
        note_dict: The note dictionary from AnkiConnect API.

    Raises:
        AssertionError: If the note structure is invalid.
    """
    assert "noteId" in note_dict, "Note missing 'noteId' field"
    assert isinstance(note_dict["noteId"], int), "'noteId' must be an integer"

    assert "modelName" in note_dict, "Note missing 'modelName' field"
    assert isinstance(note_dict["modelName"], str), "'modelName' must be a string"

    assert "fields" in note_dict, "Note missing 'fields' field"
    assert isinstance(note_dict["fields"], dict), "'fields' must be a dictionary"

    # Validate fields structure: each field should be a dict with 'value' key
    for field_name, field_data in note_dict["fields"].items():
        assert isinstance(field_data, dict), f"Field '{field_name}' must be a dict"
        assert "value" in field_data, f"Field '{field_name}' missing 'value' key"
        assert isinstance(field_data["value"], str), (
            f"Field '{field_name}' value must be a string"
        )

    assert "tags" in note_dict, "Note missing 'tags' field"
    assert isinstance(note_dict["tags"], list), "'tags' must be a list"


# Persistence layer fixtures


@pytest.fixture
def test_db_session() -> Generator[Session, None, None]:
    """Create an in-memory SQLite database for testing.

    This fixture creates a fresh database schema, yields a session for the test,
    and tears everything down afterward.

    Yields:
        SQLAlchemy session for test database operations.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def synthetic_extraction_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory with synthetic extraction files.

    Creates a structure mimicking the extractions/ directory with:
    - Valid HTML/JSON pairs with media
    - Items with missing media
    - Items with malformed JSON

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Yields:
        Path to the temporary extractions directory.
    """
    extractions = tmp_path / "extractions"
    extractions.mkdir()

    # Valid extraction 1: PeerPrep question with 2 images
    base_name_1 = "20251116_145626_PeerPrep_Q1"
    html_1 = extractions / f"{base_name_1}.html"
    json_1 = extractions / f"{base_name_1}.json"
    img_1_1 = extractions / f"{base_name_1}_img0.jpg"
    img_1_2 = extractions / f"{base_name_1}_img1.png"

    html_1.write_text("<div>Question 1 HTML</div>", encoding="utf-8")
    json_1.write_text(
        json.dumps({"question": "What is X?", "answer": "Y", "images": 2}),
        encoding="utf-8",
    )
    img_1_1.write_bytes(b"fake_jpeg_data")
    img_1_2.write_bytes(b"fake_png_data")

    # Valid extraction 2: MKSAP question with 1 image
    base_name_2 = "20251116_150929_MKSAP_19_Q2"
    html_2 = extractions / f"{base_name_2}.html"
    json_2 = extractions / f"{base_name_2}.json"
    img_2_1 = extractions / f"{base_name_2}_img0.jpg"

    html_2.write_text("<div>Question 2 HTML</div>", encoding="utf-8")
    json_2.write_text(
        json.dumps({"question": "What is Z?", "answer": "A"}),
        encoding="utf-8",
    )
    img_2_1.write_bytes(b"fake_jpeg_data_2")

    # Valid extraction 3: No images
    base_name_3 = "20251116_151354_MKSAP_19_Q3"
    html_3 = extractions / f"{base_name_3}.html"
    json_3 = extractions / f"{base_name_3}.json"

    html_3.write_text("<div>Question 3 HTML</div>", encoding="utf-8")
    json_3.write_text(
        json.dumps({"question": "Simple question?", "answer": "Simple answer"}),
        encoding="utf-8",
    )

    # Missing HTML file
    base_name_4 = "20251116_152000_PeerPrep_Q4"
    json_4 = extractions / f"{base_name_4}.json"
    json_4.write_text(
        json.dumps({"question": "Orphaned JSON?"}),
        encoding="utf-8",
    )

    # Malformed JSON
    base_name_5 = "20251116_152100_MKSAP_19_Q5"
    html_5 = extractions / f"{base_name_5}.html"
    json_5 = extractions / f"{base_name_5}.json"
    html_5.write_text("<div>Question 5 HTML</div>", encoding="utf-8")
    json_5.write_text("{ this is not valid json }", encoding="utf-8")

    yield extractions
