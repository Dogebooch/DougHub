from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from doughub.anki_client.repository import AnkiRepository
from doughub.ui.card_editor_view import CardEditorView
from doughub.ui.deck_browser_view import DeckBrowserView
from doughub.ui.deck_list_panel import DeckListPanel


class MainWindow(QMainWindow):
    """Main window for the DougHub application.

    Provides a split-pane interface with deck list on the left
    and deck browser/card editor on the right.
    """

    def __init__(
        self, repository: AnkiRepository, parent: QWidget | None = None
    ) -> None:
        """Initialize the main window.

        Args:
            repository: AnkiRepository instance for backend operations.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.repository = repository
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the main window UI components."""

        self.setWindowTitle("DougHub - Anki Deck Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Create menu bar
        menubar = self.menuBar()
        if menubar:
            file_menu = menubar.addMenu("&File")
            if file_menu:
                file_menu.addAction("&Exit", self.close)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Add toolbar with Add Note button
        toolbar = QHBoxLayout()
        self.add_note_button = QPushButton("Add Note")
        toolbar.addWidget(self.add_note_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: deck list panel
        self.deck_list_panel = DeckListPanel(self.repository)
        self.splitter.addWidget(self.deck_list_panel)

        # Right side (stacked widget for browser/editor)
        self.stacked_widget = QStackedWidget()

        # Add deck browser view
        self.deck_browser = DeckBrowserView(self.repository)
        self.stacked_widget.addWidget(self.deck_browser)

        # Add card editor view
        self.card_editor = CardEditorView(self.repository)
        self.stacked_widget.addWidget(self.card_editor)

        self.splitter.addWidget(self.stacked_widget)

        # Set initial sizes for the splitter
        self.splitter.setSizes([300, 900])

        # Add splitter to the main layout
        layout.addWidget(self.splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect signals and slots for UI interactions."""
        self.add_note_button.clicked.connect(self._on_add_note_clicked)
        self.deck_list_panel.deck_selected.connect(self._on_deck_selected)
        self.deck_browser.note_selected.connect(self._on_note_selected)
        self.card_editor.note_saved.connect(self._on_note_saved)
        self.card_editor.cancelled.connect(self._on_editor_cancelled)

    @pyqtSlot(str)
    def _on_deck_selected(self, deck_name: str) -> None:
        """Handle deck selection from the deck list panel.

        Args:
            deck_name: Name of the selected deck.
        """
        self.show_status(f"Loading deck: {deck_name}")
        self.deck_browser.load_deck(deck_name)
        self.stacked_widget.setCurrentWidget(self.deck_browser)
        self.show_status(f"Loaded deck: {deck_name}")

    @pyqtSlot(int)
    def _on_note_selected(self, note_id: int) -> None:
        """Handle note selection from the deck browser.

        Args:
            note_id: ID of the selected note.
        """
        try:
            self.show_status(f"Loading note {note_id}...")
            note = self.repository.get_note_detail(note_id)
            self.card_editor.set_edit_mode(note)
            self.stacked_widget.setCurrentWidget(self.card_editor)
            self.show_status(f"Editing note {note_id}")
        except Exception as e:
            self.show_status(f"Error loading note: {e}")

    @pyqtSlot(int)
    def _on_note_saved(self, note_id: int) -> None:
        """Handle note saved event from the editor.

        Args:
            note_id: ID of the saved note.
        """
        self.show_status(f"Note {note_id} saved successfully")
        # Refresh the deck browser if we're viewing a deck
        current_deck = self.deck_browser.get_current_deck()
        if current_deck:
            self.deck_browser.load_deck(current_deck)
        # Switch back to browser
        self.stacked_widget.setCurrentWidget(self.deck_browser)
        self.card_editor.reset()

    @pyqtSlot()
    def _on_editor_cancelled(self) -> None:
        """Handle cancel event from the editor."""
        self.stacked_widget.setCurrentWidget(self.deck_browser)
        self.card_editor.reset()
        self.show_status("Cancelled")

    @pyqtSlot()
    def _on_add_note_clicked(self) -> None:
        """Handle Add Note button click."""
        current_deck = self.deck_browser.get_current_deck()
        self.card_editor.set_add_mode(current_deck)
        self.stacked_widget.setCurrentWidget(self.card_editor)
        self.show_status("Add new note")

    def show_status(self, message: str, timeout: int = 5000) -> None:
        """Display a status message in the status bar.

        Args:
            message: Message to display.
            timeout: Duration in milliseconds (0 for permanent).
        """
        self.status_bar.showMessage(message, timeout)
