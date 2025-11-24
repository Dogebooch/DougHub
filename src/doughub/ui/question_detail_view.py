"""Question detail view for DougHub UI."""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    HorizontalSeparator,
    IconWidget,
    ProgressBar,
    SimpleCardWidget,
    SmoothScrollArea,
)

from .dto import AnswerDTO, QuestionDTO

logger = logging.getLogger(__name__)


class QuestionDetailView(QWidget):
    """A view to display all details of a single question with a placeholder."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()
        self.show_placeholder()

    def set_question(self, question_dto: QuestionDTO | None) -> None:
        """Populate the view from a QuestionDTO, or show the placeholder."""
        if not question_dto:
            self.show_placeholder()
            return

        self.placeholder_widget.setVisible(False)
        self.scroll_area.setVisible(True)

        # Clear previous content
        self._clear_layout(self.content_layout)

        # Render parent
        self._render_question_part(question_dto, "Question (Parent)")

        # Render children
        for i, child in enumerate(question_dto.children):
            self._add_separator()
            self._render_question_part(child, f"Question Part {i+1}")

    def _render_question_part(self, dto: QuestionDTO, title: str) -> None:
        # Question Text
        q_view = QTextBrowser()
        q_view.setHtml(dto.question_text_html)
        q_view.setOpenExternalLinks(True)
        # Simple auto-height adjustment could be complex, so we give it a reasonable min height
        q_view.setMinimumHeight(100)
        q_view.setFrameShape(QFrame.Shape.NoFrame)
        self.content_layout.addWidget(q_view)

        # Answers
        answers_widget = QWidget()
        answers_layout = QVBoxLayout(answers_widget)
        answers_layout.setSpacing(8)
        answers_layout.setContentsMargins(0, 0, 0, 0)
        for answer in dto.answers:
            self._add_answer_widget(answer, answers_layout)
        self.content_layout.addWidget(answers_widget)

    def _add_separator(self) -> None:
        sep = HorizontalSeparator()
        self.content_layout.addWidget(sep)

    def _add_answer_widget(self, answer_dto: AnswerDTO, layout: QVBoxLayout) -> None:
        answer_card = SimpleCardWidget()
        card_layout = QVBoxLayout(answer_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        # Header with text and optional checkmark
        header_layout = QHBoxLayout()

        answer_label = BodyLabel(answer_dto.text)
        answer_label.setWordWrap(True)
        answer_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        header_layout.addWidget(answer_label, 1)

        if answer_dto.is_correct:
            icon = IconWidget(FluentIcon.ACCEPT)
            icon.setFixedSize(16, 16)
            # Set icon color to green (success)
            icon.setStyleSheet("color: #107C10;")
            header_layout.addWidget(icon, 0)

        card_layout.addLayout(header_layout)

        if answer_dto.peer_percentage is not None:
            peer_layout = QHBoxLayout()
            progress_bar = ProgressBar()
            progress_bar.setValue(int(answer_dto.peer_percentage))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(4)
            peer_layout.addWidget(progress_bar, 1)

            percent_label = BodyLabel(f"{answer_dto.peer_percentage:.1f}%")
            peer_layout.addWidget(percent_label, 0)

            card_layout.addLayout(peer_layout)

        layout.addWidget(answer_card)

    def show_placeholder(self) -> None:
        """Show a helpful message when no question is selected."""
        self.scroll_area.setVisible(False)
        self.placeholder_widget.setVisible(True)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()

    def _init_ui(self) -> None:
        # Main layout holds placeholder and scroll area
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder
        self.placeholder_widget = QWidget(self)
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_label = BodyLabel("Select a question from the list to view its details.")
        ph_label.setObjectName("placeholderLabel")
        placeholder_layout.addWidget(ph_label)
        root_layout.addWidget(self.placeholder_widget)

        # Scroll Area for Content
        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("detailsScrollArea")
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(16, 16, 16, 16)

        self.scroll_area.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll_area)


