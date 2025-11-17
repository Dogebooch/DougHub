"""Notebook view for embedding Notesium web interface."""

import logging
from urllib.parse import quote

from PyQt6.QtCore import QUrl, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class NotebookView(QWidget):
    """Widget for displaying the Notesium notebook interface.

    Embeds a web view that loads the Notesium server interface.
    Displays an error message if Notesium is unavailable.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the notebook view.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Web engine view for Notesium
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(
            "QLabel { background-color: #fff3cd; color: #856404; "
            "padding: 15px; border: 1px solid #ffeaa7; border-radius: 4px; }"
        )
        self.error_label.hide()
        layout.addWidget(self.error_label)

    def load_url(self, url: str) -> None:
        """Load the Notesium interface at the given URL.

        Args:
            url: URL of the Notesium server.
        """
        logger.info(f"Loading Notesium at {url}")
        self.web_view.show()
        self.error_label.hide()
        self.web_view.setUrl(QUrl(url))

    def show_error(self, message: str) -> None:
        """Display an error message instead of the web view.

        Args:
            message: Error message to display.
        """
        logger.warning(f"Showing notebook error: {message}")
        self.web_view.hide()
        self.error_label.setText(message)
        self.error_label.show()

    @pyqtSlot(str)
    def open_note(self, note_path: str) -> None:
        """Navigate to a specific note in the Notesium interface.

        Constructs a URL with the file query parameter and navigates the web view.
        Assumes Notesium supports navigation via ?file=path/to/note.md query parameter.

        Args:
            note_path: Path to the note file relative to the Notesium notes directory.
        """
        if not note_path:
            logger.warning("Cannot navigate to note: empty path")
            return

        try:
            # URL-encode the note path to handle special characters
            encoded_path = quote(note_path, safe="/")

            # Construct the navigation URL with the file parameter
            # Assumes Notesium base URL is already loaded
            current_url = self.web_view.url().toString()
            if "://" not in current_url:
                logger.warning(f"Cannot navigate: invalid base URL {current_url}")
                return

            # Extract base URL (scheme + host + port)
            base_url = current_url.split("?")[0].split("#")[0]
            navigation_url = f"{base_url}?file={encoded_path}"

            logger.info(f"Navigating to note: {note_path}")
            self.web_view.setUrl(QUrl(navigation_url))
        except Exception as e:
            logger.error(f"Failed to navigate to note {note_path}: {e}")
