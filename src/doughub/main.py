"""Main entry point for DougHub PyQt6 application."""

import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub import config
from doughub.anki_client.repository import AnkiRepository
from doughub.notebook.manager import NotesiumManager
from doughub.notebook.sync import scan_and_parse_notes
from doughub.persistence.repository import QuestionRepository
from doughub.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _sync_note_metadata(repository: QuestionRepository) -> None:
    """Sync metadata from note files to the database.

    Scans all note files in NOTES_DIR and updates corresponding Question
    records with metadata from their YAML frontmatter.

    Args:
        repository: Question repository for database operations.
    """
    notes_dir = Path(config.NOTES_DIR)
    if not notes_dir.exists():
        logger.info(f"Notes directory does not exist: {notes_dir}, skipping metadata sync")
        return

    logger.info("Starting metadata sync from note files...")
    sync_count = 0
    error_count = 0

    try:
        for metadata in scan_and_parse_notes(notes_dir):
            try:
                if repository.update_question_from_metadata(metadata):
                    sync_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to update question from metadata: {e}", exc_info=True)

        # Commit all updates
        repository.commit()
        logger.info(f"Metadata sync complete: {sync_count} questions updated, {error_count} errors")

    except Exception as e:
        logger.error(f"Metadata sync failed: {e}", exc_info=True)
        repository.rollback()


def main() -> int:
    """Launch the DougHub UI application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("DougHub")

    # Initialize Notesium manager
    notesium_manager = NotesiumManager()

    # Initialize database session for persistence
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    question_repository = QuestionRepository(db_session)

    # Sync metadata from note files to database
    _sync_note_metadata(question_repository)

    try:
        # Initialize backend
        repository = AnkiRepository()

        # Test connection
        try:
            repository.get_deck_names()
        except Exception as e:
            logger.error(f"Failed to connect to Anki: {e}")
            QMessageBox.critical(
                None,
                "Connection Error",
                f"Could not connect to AnkiConnect.\n\n"
                f"Please ensure Anki is running and AnkiConnect is installed.\n\n"
                f"Error: {e}",
            )
            db_session.close()
            return 1

        # Start Notesium (non-blocking, failures are logged but don't stop app)
        logger.info("Starting Notesium server...")
        if not notesium_manager.start():
            logger.warning("Notesium failed to start. Notebook features will be unavailable.")

        # Create and show main window
        window = MainWindow(repository, notesium_manager, question_repository)
        window.show()

        try:
            return app.exec()
        finally:
            # Ensure Notesium is stopped when app closes
            logger.info("Shutting down Notesium...")
            notesium_manager.stop()
            # Close database session
            db_session.close()

    except Exception as e:
        logger.exception("Fatal error during application startup")
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"An unexpected error occurred:\n\n{e}",
        )
        notesium_manager.stop()
        db_session.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
