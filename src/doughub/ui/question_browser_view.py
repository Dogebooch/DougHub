import logging
import re

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    ListWidget,
    RoundMenu,
    SearchLineEdit,
)
from sqlalchemy.orm import Session, joinedload

from doughub.models import Question

logger = logging.getLogger(__name__)


def strip_html(html_string: str) -> str:
    """Strips HTML tags and collapses whitespace."""
    # Remove HTML tags
    text = re.sub("<[^<]+?>", "", html_string)
    # Collapse whitespace and strip
    text = " ".join(text.split()).strip()
    return text


class QuestionListItem(QWidget):
    """A custom widget for displaying a question in the QuestionBrowserView list."""

    def __init__(self, question_id: int, source: str, raw_html: str, has_children: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.question_id = question_id
        self.source = source
        self.raw_html = raw_html
        self.has_children = has_children
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # Top line: Source and Question ID
        top_layout = QHBoxLayout()
        self.source_label = CaptionLabel(f"{self.source} | Q{self.question_id}")
        self.source_label.setStyleSheet("color: --ThemeColorLight1;")
        top_layout.addWidget(self.source_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Bottom line: Question snippet
        stripped_text = strip_html(self.raw_html)
        snippet = stripped_text[:120]
        if len(stripped_text) > 120:
            snippet += "..."
        self.snippet_label = BodyLabel(snippet)
        self.snippet_label.setWordWrap(True)
        layout.addWidget(self.snippet_label)

    def full_text(self) -> str:
        return f"{self.source} Q{self.question_id} {strip_html(self.raw_html)}"


class QuestionBrowserView(QWidget):
    """A widget to list and filter extracted questions."""

    question_selected = pyqtSignal(int)
    manage_group_requested = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.search_bar = SearchLineEdit()
        self.search_bar.setPlaceholderText("Search questions...")
        self.search_bar.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_bar)

        self.empty_label = BodyLabel("No questions found.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setHidden(True)
        layout.addWidget(self.empty_label)

        self.list_widget = ListWidget()
        self.list_widget.currentItemChanged.connect(self._on_item_changed)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        # The ListWidget will be responsible for drawing the items, no borders needed
        self.list_widget.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.list_widget)

    def load_questions(self, session: Session) -> None:
        """Loads all questions from the database into the list."""
        self.list_widget.clear()
        self.empty_label.setHidden(True)
        self.list_widget.setHidden(False)

        try:
            questions = (
                session.query(Question)
                .options(joinedload(Question.source), joinedload(Question.children))
                .filter(Question.parent_id.is_(None))
                .all()
            )

            for question in questions:
                topic = question.source.name if question.source else "Unknown"
                has_children = bool(question.children)

                custom_widget = QuestionListItem(
                    question_id=question.question_id,
                    source=topic,
                    raw_html=question.raw_html,
                    has_children=has_children,
                )

                item = QListWidgetItem(self.list_widget)
                # Store the full text for searching
                item.setData(Qt.ItemDataRole.UserRole, custom_widget.full_text())
                # Set the size hint to the widget's size hint
                item.setSizeHint(custom_widget.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, custom_widget)

            if not questions:
                self.list_widget.setHidden(True)
                self.empty_label.setText("No questions found.")
                self.empty_label.setHidden(False)

        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            self.list_widget.setHidden(True)
            self.empty_label.setText("An error occurred while loading questions.")
            self.empty_label.setHidden(False)

    def _show_context_menu(self, position: QPoint) -> None:
        item = self.list_widget.itemAt(position)
        if not item:
            return

        widget = self.list_widget.itemWidget(item)
        if not isinstance(widget, QuestionListItem):
            return

        if widget.has_children:
            menu = RoundMenu(parent=self)
            manage_action = menu.addAction("Manage Group...")
            action = menu.exec(self.list_widget.mapToGlobal(position))
            if action == manage_action:
                self.manage_group_requested.emit(widget.question_id)

    def _filter_items(self, text: str) -> None:
        """Filters the list widget items based on the search text."""
        search_text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item is None:
                continue

            # Search in the stored full text (UserRole)
            item_text = item.data(Qt.ItemDataRole.UserRole)
            if item_text is None:
                item.setHidden(True)
                continue
            item.setHidden(search_text not in item_text.lower())

    def _on_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if current:
            widget = self.list_widget.itemWidget(current)
            if isinstance(widget, QuestionListItem):
                self.question_selected.emit(widget.question_id)
