import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import Session, joinedload

from doughub.models import Question

logger = logging.getLogger(__name__)


class QuestionBrowserView(QWidget):
    """A widget to list and filter extracted questions."""

    question_selected = pyqtSignal(int)
    manage_group_requested = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search questions...")
        self.search_bar.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_bar)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_item_changed)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

    def load_questions(self, session: Session) -> None:
        """Loads all questions from the database into the list."""
        self.list_widget.clear()
        try:
            questions = session.query(Question).options(
                joinedload(Question.source),
                joinedload(Question.children)
            ).filter(Question.parent_id.is_(None)).all()

            for question in questions:
                topic = question.source.name if question.source else "Unknown"
                num_parts = len(question.children) + 1
                display_text = f"Q {question.question_id} ({topic}) - [{num_parts} parts]"

                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, question.question_id)
                # Store the full text for searching (maybe strip HTML here too ideally)
                item.setData(Qt.ItemDataRole.UserRole + 1, question.raw_html)
                # Store if it has children for context menu
                item.setData(Qt.ItemDataRole.UserRole + 2, bool(question.children))
                self.list_widget.addItem(item)
        except Exception as e:
            logger.error(f"Error loading questions: {e}")

    def _show_context_menu(self, position) -> None:
        item = self.list_widget.itemAt(position)
        if not item:
            return

        has_children = item.data(Qt.ItemDataRole.UserRole + 2)
        if has_children:
            menu = QMenu()
            manage_action = menu.addAction("Manage Group...")
            action = menu.exec(self.list_widget.mapToGlobal(position))
            if action == manage_action:
                question_id = item.data(Qt.ItemDataRole.UserRole)
                self.manage_group_requested.emit(question_id)

    def _filter_items(self, text: str) -> None:
        """Filters the list widget items based on the search text."""
        search_text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item is None:
                continue
            # Search in the stored full text (UserRole + 1) or display text
            item_text = item.data(Qt.ItemDataRole.UserRole + 1) or item.text()
            item.setHidden(search_text not in item_text.lower())

    def _on_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if current:
            question_id = current.data(Qt.ItemDataRole.UserRole)
            self.question_selected.emit(question_id)
