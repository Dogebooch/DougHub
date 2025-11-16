"""Deck list panel for DougHub UI."""

import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListWidget, QVBoxLayout, QWidget

from doughub.anki_client.repository import AnkiRepository

logger = logging.getLogger(__name__)


class DeckListPanel(QWidget):
    """Panel displaying a list of all Anki decks.

    Emits a signal when a deck is selected by the user.
    """

    deck_selected = pyqtSignal(str)  # Emits deck name when selected

    def __init__(self, repository: AnkiRepository, parent: QWidget | None = None) -> None:
        """Initialize the deck list panel.

        Args:
            repository: AnkiRepository instance for fetching decks.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.repository = repository
        self._setup_ui()
        self._connect_signals()
        self.refresh()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Create list widget
        self.deck_list = QListWidget()
        layout.addWidget(self.deck_list)

        # Set layout margins
        layout.setContentsMargins(0, 0, 0, 0)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self.deck_list.currentTextChanged.connect(self._on_deck_selection_changed)

    def _on_deck_selection_changed(self, deck_name: str) -> None:
        """Handle deck selection change.

        Args:
            deck_name: Name of the selected deck.
        """
        if deck_name:
            logger.debug(f"Deck selected: {deck_name}")
            self.deck_selected.emit(deck_name)

    def refresh(self) -> None:
        """Refresh the deck list from the repository."""
        try:
            logger.info("Fetching deck names from repository")
            deck_names = self.repository.get_deck_names()

            # Clear and populate the list
            self.deck_list.clear()
            self.deck_list.addItems(deck_names)

            logger.info(f"Loaded {len(deck_names)} decks")

        except Exception as e:
            logger.error(f"Failed to load decks: {e}")
            self.deck_list.clear()
            self.deck_list.addItem(f"Error loading decks: {e}")
