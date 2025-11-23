"""Question detail view for DougHub UI."""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
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
        # Add title
        header = self._create_section_label(title)
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; color: #2c3e50;")
        self.content_layout.addWidget(header)

        # Question Text
        q_view = QTextBrowser()
        q_view.setHtml(dto.question_text_html)
        q_view.setOpenExternalLinks(True)
        # Simple auto-height adjustment could be complex, so we give it a reasonable min height
        q_view.setMinimumHeight(100)
        self.content_layout.addWidget(q_view)

        # Image
        if dto.image_path:
            try:
                pixmap = QPixmap(dto.image_path)
                if not pixmap.isNull():
                    img_label = QLabel()
                    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    img_label.setPixmap(
                        pixmap.scaled(
                            self.scroll_area.width() - 50,
                            400,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    self.content_layout.addWidget(img_label)
                else:
                    logger.warning(f"Failed to load image: {dto.image_path}")
            except Exception as e:
                logger.error(f"Error loading image {dto.image_path}: {e}")

        # Answers
        self.content_layout.addWidget(self._create_section_label("Answers"))
        answers_widget = QWidget()
        answers_layout = QVBoxLayout(answers_widget)
        answers_layout.setSpacing(10)
        for answer in dto.answers:
            self._add_answer_widget(answer, answers_layout)
        self.content_layout.addWidget(answers_widget)

        # Explanation
        self.content_layout.addWidget(self._create_section_label("Explanation"))
        exp_view = QTextBrowser()
        exp_view.setHtml(dto.explanation_html)
        exp_view.setOpenExternalLinks(True)
        exp_view.setMinimumHeight(100)
        self.content_layout.addWidget(exp_view)

    def _add_separator(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #bdc3c7; margin: 20px 0;")
        self.content_layout.addWidget(line)

    def _add_answer_widget(self, answer_dto: AnswerDTO, layout: QVBoxLayout) -> None:
        answer_frame = QFrame()
        answer_frame.setObjectName("answerFrame")
        if answer_dto.is_correct:
            answer_frame.setProperty("correct", True)

        frame_layout = QVBoxLayout(answer_frame)
        answer_label = QLabel(answer_dto.text)
        answer_label.setWordWrap(True)
        answer_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        frame_layout.addWidget(answer_label)

        if answer_dto.peer_percentage is not None:
            peer_layout = QHBoxLayout()
            progress_bar = QProgressBar()
            progress_bar.setValue(int(answer_dto.peer_percentage))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(12)
            peer_layout.addWidget(progress_bar, 1)  # Stretch factor

            percent_label = QLabel(f"{answer_dto.peer_percentage:.1f}%")
            peer_layout.addWidget(percent_label, 0)

            frame_layout.addLayout(peer_layout)

        layout.addWidget(answer_frame)

    def show_placeholder(self) -> None:
        """Show a helpful message when no question is selected."""
        self.scroll_area.setVisible(False)
        self.placeholder_widget.setVisible(True)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _init_ui(self) -> None:
        # Main layout holds placeholder and scroll area
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder
        self.placeholder_widget = QWidget(self)
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_label = QLabel("Select a question from the list to view its details.")
        ph_label.setObjectName("placeholderLabel")
        placeholder_layout.addWidget(ph_label)
        root_layout.addWidget(self.placeholder_widget)

        # Scroll Area for Content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("detailsScrollArea")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll_area)

    def _create_section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionHeader")
        return label
