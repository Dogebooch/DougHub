"""Main entry point for DougHub PyQt6 application."""

import logging
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from doughub.anki_client.repository import AnkiRepository
from doughub.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


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
            return 1

        # Create and show main window
        window = MainWindow(repository)
        window.show()

        return app.exec()

    except Exception as e:
        logger.exception("Fatal error during application startup")
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"An unexpected error occurred:\n\n{e}",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
