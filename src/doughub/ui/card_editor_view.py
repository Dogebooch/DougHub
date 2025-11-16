"""Card editor view for DougHub UI."""

import logging

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from doughub.anki_client.repository import AnkiRepository
from doughub.models import Note

logger = logging.getLogger(__name__)


class CardEditorView(QWidget):
    """View for adding and editing Anki notes.

    Provides a form with dynamic field generation based on the selected
    note type (model).
    """

    note_saved = pyqtSignal(int)  # Emits note ID when saved
    cancelled = pyqtSignal()  # Emits when cancel is clicked

    def __init__(self, repository: AnkiRepository, parent: QWidget | None = None) -> None:
        """Initialize the card editor view.

        Args:
            repository: AnkiRepository instance for backend operations.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.repository = repository
        self._mode: str = "add"  # "add" or "edit"
        self._current_note_id: int | None = None
        self._field_widgets: dict[str, QTextEdit | QLineEdit] = {}
        self._setup_ui()
        self._connect_signals()
        self._load_decks_and_models()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)

        # Title label
        self.title_label = QLabel("Add Note")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        # Deck and model selection
        selection_layout = QFormLayout()

        self.deck_combo = QComboBox()
        selection_layout.addRow("Deck:", self.deck_combo)

        self.model_combo = QComboBox()
        selection_layout.addRow("Note Type:", self.model_combo)

        main_layout.addLayout(selection_layout)

        # Scrollable area for dynamic fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.fields_widget = QWidget()
        self.fields_layout = QFormLayout(self.fields_widget)
        scroll_area.setWidget(self.fields_widget)

        main_layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

    def _load_decks_and_models(self) -> None:
        """Load deck and model names from the repository."""
        try:
            # Load decks
            deck_names = self.repository.get_deck_names()
            self.deck_combo.addItems(deck_names)

            # Load models
            model_names = self.repository.get_model_names()
            self.model_combo.addItems(model_names)

            logger.info("Loaded decks and models for editor")

        except Exception as e:
            logger.error(f"Failed to load decks/models: {e}")

    @pyqtSlot(str)
    def _on_model_changed(self, model_name: str) -> None:
        """Handle model selection change.

        Args:
            model_name: Name of the selected model.
        """
        if not model_name:
            return

        try:
            # Get field names for the selected model
            field_names = self.repository.get_model_field_names(model_name)
            self._create_field_widgets(field_names)

            logger.debug(f"Generated fields for model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to get fields for model '{model_name}': {e}")

    def _create_field_widgets(self, field_names: list[str]) -> None:
        """Create input widgets for each field.

        Args:
            field_names: List of field names to create widgets for.
        """
        # Clear existing field widgets
        self._field_widgets.clear()
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()

        # Create new field widgets
        for field_name in field_names:
            # Use QTextEdit for multiline fields, QLineEdit for single-line
            # This is a simple heuristic; could be improved
            widget: QTextEdit | QLineEdit
            if "Back" in field_name or len(field_names) <= 2:
                widget = QTextEdit()
                widget.setMaximumHeight(100)
            else:
                widget = QLineEdit()

            self._field_widgets[field_name] = widget
            self.fields_layout.addRow(f"{field_name}:", widget)

    def _get_field_values(self) -> dict[str, str]:
        """Get the current field values from the form.

        Returns:
            Dictionary mapping field names to their values.
        """
        field_values = {}
        for field_name, widget in self._field_widgets.items():
            if isinstance(widget, QTextEdit):
                field_values[field_name] = widget.toPlainText()
            else:
                field_values[field_name] = widget.text()
        return field_values

    def _set_field_values(self, field_values: dict[str, str]) -> None:
        """Set the field values in the form.

        Args:
            field_values: Dictionary mapping field names to values.
        """
        for field_name, value in field_values.items():
            if field_name in self._field_widgets:
                widget = self._field_widgets[field_name]
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)

    @pyqtSlot()
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        try:
            deck_name = self.deck_combo.currentText()
            model_name = self.model_combo.currentText()
            field_values = self._get_field_values()

            if not deck_name or not model_name:
                logger.warning("Deck or model not selected")
                return

            if self._mode == "add":
                # Create new note
                note_id = self.repository.add_note(deck_name, model_name, field_values)
                logger.info(f"Created note {note_id}")
                self.note_saved.emit(note_id)

            elif self._mode == "edit" and self._current_note_id is not None:
                # Update existing note
                self.repository.update_note_fields(self._current_note_id, field_values)
                logger.info(f"Updated note {self._current_note_id}")
                self.note_saved.emit(self._current_note_id)

        except Exception as e:
            logger.error(f"Failed to save note: {e}")

    @pyqtSlot()
    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self.cancelled.emit()

    def set_add_mode(self, deck_name: str | None = None) -> None:
        """Switch to add mode for creating a new note.

        Args:
            deck_name: Optional deck name to pre-select.
        """
        self._mode = "add"
        self._current_note_id = None
        self.title_label.setText("Add Note")
        self.save_button.setText("Save")

        # Clear all fields
        for widget in self._field_widgets.values():
            if isinstance(widget, QTextEdit):
                widget.clear()
            else:
                widget.setText("")

        # Set deck if provided
        if deck_name:
            index = self.deck_combo.findText(deck_name)
            if index >= 0:
                self.deck_combo.setCurrentIndex(index)

    def set_edit_mode(self, note: Note) -> None:
        """Switch to edit mode for modifying an existing note.

        Args:
            note: The Note object to edit.
        """
        self._mode = "edit"
        self._current_note_id = note.note_id
        self.title_label.setText(f"Edit Note (ID: {note.note_id})")
        self.save_button.setText("Update")

        # Set model (which will generate fields)
        model_index = self.model_combo.findText(note.model_name)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)

        # Set field values
        self._set_field_values(note.fields)

        # Disable model and deck selection in edit mode
        self.model_combo.setEnabled(False)
        self.deck_combo.setEnabled(False)

    def reset(self) -> None:
        """Reset the editor to default add mode."""
        self.model_combo.setEnabled(True)
        self.deck_combo.setEnabled(True)
        self.set_add_mode()
