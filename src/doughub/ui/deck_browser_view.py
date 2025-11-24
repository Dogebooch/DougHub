"""Deck browser view for DougHub UI."""

import logging

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import TableView

from doughub.anki_client.repository import AnkiRepository
from doughub.models import Note
from doughub.persistence.repository import QuestionRepository

logger = logging.getLogger(__name__)


class NotesTableModel(QAbstractTableModel):
    """Table model for displaying Anki notes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the notes table model.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._notes: list[Note] = []
        self._headers = ["Note ID", "Model", "Fields", "Tags"]

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of rows in the model.

        Args:
            parent: Parent model index (unused for table).

        Returns:
            Number of notes.
        """
        if parent is None:
            parent = QModelIndex()
        if parent.isValid():
            return 0
        return len(self._notes)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of columns in the model.

        Args:
            parent: Parent model index (unused for table).

        Returns:
            Number of columns.
        """
        if parent is None:
            parent = QModelIndex()
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | None:
        """Return data for a specific cell.

        Args:
            index: Model index specifying row and column.
            role: Data role (display, edit, etc.).

        Returns:
            Cell data as string, or None.
        """
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        note = self._notes[index.row()]
        column = index.column()

        if column == 0:
            return str(note.note_id)
        elif column == 1:
            return note.model_name
        elif column == 2:
            # Display field values as a summary
            field_summary = ", ".join(
                f"{k}: {v[:50]}..." if len(v) > 50 else f"{k}: {v}"
                for k, v in note.fields.items()
            )
            return field_summary
        elif column == 3:
            return ", ".join(note.tags)

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        """Return header data for columns.

        Args:
            section: Column or row index.
            orientation: Horizontal (columns) or vertical (rows).
            role: Data role.

        Returns:
            Header label as string, or None.
        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

        return str(section + 1)

    def set_notes(self, notes: list[Note]) -> None:
        """Update the model with a new list of notes.

        Args:
            notes: List of Note objects to display.
        """
        self.beginResetModel()
        self._notes = notes
        self.endResetModel()

    def get_note(self, row: int) -> Note | None:
        """Get the note at a specific row.

        Args:
            row: Row index.

        Returns:
            Note object, or None if row is invalid.
        """
        if 0 <= row < len(self._notes):
            return self._notes[row]
        return None


class DeckBrowserView(QWidget):
    """View for browsing notes in a selected deck.

    Displays notes in a table and emits signals when notes are selected.
    """

    note_selected = pyqtSignal(int)  # Emits note ID when double-clicked
    note_ready_for_navigation = pyqtSignal(str)  # Emits note path when ready for notebook navigation

    def __init__(
        self,
        repository: AnkiRepository,
        question_repository: QuestionRepository | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the deck browser view.

        Args:
            repository: AnkiRepository instance for fetching notes.
            question_repository: Optional QuestionRepository for notebook integration.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.repository = repository
        self.question_repository = question_repository
        self._current_deck: str | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Create table view and model
        self.model = NotesTableModel(self)
        self.table_view = TableView(self)
        self.table_view.setModel(self.model)

        # Configure table appearance
        self.table_view.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(TableView.SelectionMode.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(False)

        # Enable border and rounded corners
        self.table_view.setBorderVisible(True)
        self.table_view.setBorderRadius(8)
        self.table_view.setWordWrap(False)

        # Set column stretch
        header = self.table_view.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        layout.addWidget(self.table_view)
        layout.setContentsMargins(0, 0, 0, 0)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self.table_view.doubleClicked.connect(self._on_row_double_clicked)

    def _on_row_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click on a table row.

        Ensures a markdown note exists for the selected Anki note,
        then emits signals for both editor opening and notebook navigation.

        Args:
            index: Model index of the clicked cell.
        """
        note = self.model.get_note(index.row())
        if note:
            logger.debug(f"Note double-clicked: {note.note_id}")

            # Ensure a markdown note exists for this Anki note (if question_repository available)
            if self.question_repository:
                try:
                    # For Phase 2, use note_id as a temporary question identifier
                    # This assumes a 1:1 mapping or that ensure_note_for_question creates as needed
                    note_path = self.question_repository.ensure_note_for_question(note.note_id)

                    # Emit navigation signal after note file is guaranteed to exist
                    if note_path:
                        logger.debug(f"Note ready for navigation: {note_path}")
                        self.note_ready_for_navigation.emit(note_path)
                except Exception as e:
                    logger.error(f"Failed to ensure note for {note.note_id}: {e}")

            # Emit the original signal for editor view
            self.note_selected.emit(note.note_id)

    def load_deck(self, deck_name: str) -> None:
        """Load and display notes from a specific deck.

        Args:
            deck_name: Name of the deck to load.
        """
        try:
            logger.info(f"Loading notes from deck: {deck_name}")
            self._current_deck = deck_name

            # Fetch notes from repository
            notes = self.repository.list_notes_in_deck(deck_name, limit=100)

            # Update the table model
            self.model.set_notes(notes)

            logger.info(f"Loaded {len(notes)} notes from deck '{deck_name}'")

        except Exception as e:
            logger.error(f"Failed to load deck '{deck_name}': {e}")
            self.model.set_notes([])

    def get_current_deck(self) -> str | None:
        """Get the name of the currently displayed deck.

        Returns:
            Deck name, or None if no deck is loaded.
        """
        return self._current_deck
