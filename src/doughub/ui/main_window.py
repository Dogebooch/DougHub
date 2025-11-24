from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import PrimaryPushButton

from doughub.anki_client.repository import AnkiRepository
from doughub.notebook.manager import NotesiumManager
from doughub.persistence.repository import QuestionRepository
from doughub.services import HealthMonitor
from doughub.ui.card_editor_view import CardEditorView
from doughub.ui.deck_browser_view import DeckBrowserView
from doughub.ui.deck_list_panel import DeckListPanel
from doughub.ui.diagnostics_view import DiagnosticsView
from doughub.ui.dto import QuestionDetailDTO
from doughub.ui.manage_group_dialog import ManageGroupDialog
from doughub.ui.notebook_view import NotebookView
from doughub.ui.question_browser_view import QuestionBrowserView
from doughub.ui.question_detail_view import QuestionDetailView
from doughub.utils.logging import QtTextEditHandler


class MainWindow(QMainWindow):
    """Main window for the DougHub application.

    Provides a tabbed interface with Anki deck management and
    extracted question browsing.
    """

    def __init__(
        self,
        repository: AnkiRepository,
        notesium_manager: NotesiumManager,
        question_repository: QuestionRepository | None = None,
        log_handler: QtTextEditHandler | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the main window.

        Args:
            repository: AnkiRepository instance for backend operations.
            notesium_manager: NotesiumManager instance for notebook features.
            question_repository: Optional QuestionRepository for notebook integration.
            log_handler: Optional logging handler for diagnostics view.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.repository = repository
        self.notesium_manager = notesium_manager
        self.question_repository = question_repository
        self.log_handler = log_handler
        self._setup_ui()
        self._connect_signals()

        # Set up health monitoring
        self.health_monitor = HealthMonitor(
            anki_repository=repository,
            notesium_manager=notesium_manager,
            parent=self
        )
        self.health_monitor.ankiStatusChanged.connect(self._on_anki_status_changed)
        self.health_monitor.notesiumStatusChanged.connect(self._on_notesium_status_changed)
        self.health_monitor.start()

        # Load questions if repository is available
        if self.question_repository:
            self.question_browser.load_questions(self.question_repository.session)

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

        # Main Tab Widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # --- Anki Tab ---
        anki_tab = QWidget()
        anki_layout = QVBoxLayout(anki_tab)
        anki_layout.setContentsMargins(10, 10, 10, 10)

        # Add toolbar with Add Note button (Anki specific)
        toolbar = QHBoxLayout()
        self.add_note_button = PrimaryPushButton("Add Note")
        toolbar.addWidget(self.add_note_button)
        toolbar.addStretch()
        anki_layout.addLayout(toolbar)

        # Anki splitter (horizontal: left deck list, middle browser/editor, right notebook)
        self.anki_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: deck list panel
        self.deck_list_panel = DeckListPanel(self.repository)
        self.anki_splitter.addWidget(self.deck_list_panel)

        # Middle: stacked widget for browser/editor
        self.stacked_widget = QStackedWidget()

        # Add deck browser view
        self.deck_browser = DeckBrowserView(
            self.repository, self.question_repository
        )
        self.stacked_widget.addWidget(self.deck_browser)

        # Add card editor view
        self.card_editor = CardEditorView(self.repository)
        self.stacked_widget.addWidget(self.card_editor)

        self.anki_splitter.addWidget(self.stacked_widget)

        # Right side: notebook view
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Creating NotebookView widget...")
        self.notebook_view = NotebookView()
        logger.info("Adding NotebookView to splitter...")
        self.anki_splitter.addWidget(self.notebook_view)

        # Initialize notebook view based on Notesium status
        logger.info("Checking Notesium health status...")
        if self.notesium_manager.is_healthy():
            logger.info(f"Notesium is healthy, loading URL: {self.notesium_manager.url}")
            self.notebook_view.load_url(self.notesium_manager.url)
        else:
            logger.warning("Notesium is not healthy, showing error message in UI")
            self.notebook_view.show_error(
                "Notebook features are unavailable.\n\n"
                "The Notesium server failed to start. Please ensure:\n"
                "• Notesium binary is installed and in your PATH\n"
                "  Download from: https://github.com/alonswartz/notesium/releases/latest\n"
                "• Port 3030 is available\n\n"
                "Check the logs for more details."
            )

        # Set initial sizes for the splitter (deck list: 250, browser: 550, notebook: 400)
        self.anki_splitter.setSizes([250, 550, 400])

        anki_layout.addWidget(self.anki_splitter)
        self.tab_widget.addTab(anki_tab, "Anki Decks")

        # --- Extracted Questions Tab ---
        questions_tab = QWidget()
        questions_layout = QVBoxLayout(questions_tab)
        questions_layout.setContentsMargins(10, 10, 10, 10)

        self.questions_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.question_browser = QuestionBrowserView()
        self.questions_splitter.addWidget(self.question_browser)

        self.question_detail_view = QuestionDetailView()
        self.questions_splitter.addWidget(self.question_detail_view)

        self.questions_splitter.setSizes([300, 900])

        questions_layout.addWidget(self.questions_splitter)
        self.tab_widget.addTab(questions_tab, "Extracted Questions")

        # --- Diagnostics Tab ---
        diagnostics_tab = QWidget()
        diagnostics_layout = QVBoxLayout(diagnostics_tab)
        diagnostics_layout.setContentsMargins(10, 10, 10, 10)

        self.diagnostics_view = DiagnosticsView()
        diagnostics_layout.addWidget(self.diagnostics_view)
        self.tab_widget.addTab(diagnostics_tab, "Diagnostics")

        # Connect log handler to diagnostics view
        if self.log_handler:
            self.log_handler.set_widget(self.diagnostics_view.get_log_widget())

        # Create status bar with service indicators
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add service status indicators
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 0, 5, 0)
        status_layout.setSpacing(15)

        # Anki status
        self.anki_status_indicator = QLabel("●")
        self.anki_status_indicator.setStyleSheet("color: gray; font-size: 14px;")
        self.anki_status_indicator.setToolTip("AnkiConnect: Unknown")
        status_layout.addWidget(QLabel("Anki:"))
        status_layout.addWidget(self.anki_status_indicator)

        # Notesium status
        self.notesium_status_indicator = QLabel("●")
        self.notesium_status_indicator.setStyleSheet("color: gray; font-size: 14px;")
        self.notesium_status_indicator.setToolTip("Notesium: Unknown")
        status_layout.addWidget(QLabel("Notesium:"))
        status_layout.addWidget(self.notesium_status_indicator)

        self.status_bar.addPermanentWidget(status_widget)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect signals and slots for UI interactions."""
        self.add_note_button.clicked.connect(self._on_add_note_clicked)
        self.deck_list_panel.deck_selected.connect(self._on_deck_selected)
        self.deck_browser.note_selected.connect(self._on_note_selected)
        self.deck_browser.note_ready_for_navigation.connect(self.notebook_view.open_note)
        self.card_editor.note_saved.connect(self._on_note_saved)
        self.card_editor.cancelled.connect(self._on_editor_cancelled)

        self.question_browser.question_selected.connect(self._on_question_selected)
        self.question_browser.manage_group_requested.connect(self._on_manage_group_requested)

    @pyqtSlot(int)
    def _on_manage_group_requested(self, question_id: int) -> None:
        """Handle request to manage a question group."""
        if not self.question_repository:
            return

        question = self.question_repository.get_question_by_id(question_id)
        if not question:
            return

        dialog = ManageGroupDialog(question, self)
        dialog.unlink_requested.connect(self._on_unlink_question)
        dialog.exec()

    @pyqtSlot(int)
    def _on_unlink_question(self, child_id: int) -> None:
        """Handle request to unlink a child question."""
        if not self.question_repository:
            return

        try:
            # Use the session from repository
            session = self.question_repository.session
            # We can fetch the child directly using the repository helper if available,
            # or query the session. Since we have the ID, let's use the repository.
            child = self.question_repository.get_question_by_id(child_id)
            if child:
                child.parent_id = None
                session.commit()
                self.show_status(f"Unlinked question {child_id}")
                # Refresh browser
                self.question_browser.load_questions(session)
        except Exception as e:
            self.show_status(f"Error unlinking question: {e}")
            import logging
            logging.getLogger(__name__).error(f"Error unlinking question {child_id}: {e}", exc_info=True)

    @pyqtSlot(int)
    def _on_question_selected(self, question_id: int) -> None:
        """Handle question selection from the browser view."""
        if not self.question_repository:
            return

        try:
            question = self.question_repository.get_question_by_id(question_id)
            if question:
                detail_dto = QuestionDetailDTO.from_model(question)
                self.question_detail_view.populate_view(detail_dto)
            else:
                self.question_detail_view.populate_view(QuestionDetailDTO.empty())
        except Exception as e:
            self.show_status(f"Error loading question details: {e}")
            import logging
            logging.getLogger(__name__).error(f"Error loading question {question_id}: {e}", exc_info=True)
            # On error, show empty view to avoid stale state
            self.question_detail_view.populate_view(QuestionDetailDTO.empty())

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

    @pyqtSlot(bool, str)
    def _on_anki_status_changed(self, is_healthy: bool, status_message: str) -> None:
        """Handle AnkiConnect status change.

        Args:
            is_healthy: Whether Anki is healthy.
            status_message: Status description.
        """
        if is_healthy:
            self.anki_status_indicator.setStyleSheet("color: green; font-size: 14px;")
            self.anki_status_indicator.setToolTip(f"AnkiConnect: {status_message}")
        else:
            self.anki_status_indicator.setStyleSheet("color: red; font-size: 14px;")
            self.anki_status_indicator.setToolTip(f"AnkiConnect: {status_message}")

    @pyqtSlot(bool, str)
    def _on_notesium_status_changed(self, is_healthy: bool, status_message: str) -> None:
        """Handle Notesium status change.

        Args:
            is_healthy: Whether Notesium is healthy.
            status_message: Status description.
        """
        if is_healthy:
            self.notesium_status_indicator.setStyleSheet("color: green; font-size: 14px;")
            self.notesium_status_indicator.setToolTip(f"Notesium: {status_message}")
        else:
            self.notesium_status_indicator.setStyleSheet("color: red; font-size: 14px;")
            self.notesium_status_indicator.setToolTip(f"Notesium: {status_message}")
