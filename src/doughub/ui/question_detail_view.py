"""Question detail view for DougHub UI."""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    FluentIcon,
    IconWidget,
    PillPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
)

from .dto import AnswerDTO, QuestionDetailDTO

logger = logging.getLogger(__name__)


class QuestionDetailView(QWidget):
    """Refactored view to display comprehensive, structured medical question details.

    This view presents:
    1. Question section: Clinical vignette and question stem with clear typography
    2. Answers section: Interactive cards showing choices, peer stats, and correctness
    3. Explanation section: Educational objective, key points, and full explanation

    Designed following the DougHub UI/UX Algorithmic Design Standard with
    theme-aware components, 8-pt grid spacing, and F-pattern layout flow.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()
        self.show_placeholder()

    def populate_view(self, data: QuestionDetailDTO) -> None:
        """Populate the view from a QuestionDetailDTO.

        This method clears any previous content and dynamically builds
        the entire view with the provided structured data.

        Args:
            data: QuestionDetailDTO containing all question details
        """
        self.placeholder_widget.setVisible(False)
        self.scroll_area.setVisible(True)

        # Clear previous content
        self._clear_layout(self.content_layout)

        # Section 1: Question Display
        self._build_question_section(data)

        # Add spacing between sections (16px following 8-pt grid)
        self.content_layout.addSpacing(16)

        # Section 2: Answer Choices List
        self._build_answers_section(data)

        # Add spacing between sections
        self.content_layout.addSpacing(16)

        # Section 3: Explanation Section
        self._build_explanation_section(data)

        # Add stretch to push content to top
        self.content_layout.addStretch(1)

    def _build_question_section(self, data: QuestionDetailDTO) -> None:
        """Build the Question section with vignette and stem."""
        # Section title
        section_title = TitleLabel("Question")
        self.content_layout.addWidget(section_title)
        self.content_layout.addSpacing(8)

        # Vignette (if present)
        if data.vignette:
            vignette_label = BodyLabel(data.vignette)
            vignette_label.setWordWrap(True)
            vignette_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self.content_layout.addWidget(vignette_label)
            self.content_layout.addSpacing(8)

        # Question stem (bold, prominent)
        if data.stem:
            stem_label = SubtitleLabel(data.stem)
            stem_label.setWordWrap(True)
            stem_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            # Make it bold for emphasis
            font = stem_label.font()
            font.setBold(True)
            stem_label.setFont(font)
            self.content_layout.addWidget(stem_label)

    def _build_answers_section(self, data: QuestionDetailDTO) -> None:
        """Build the Answers section with cards for each choice."""
        # Section title
        section_title = TitleLabel("Answer Choices")
        self.content_layout.addWidget(section_title)
        self.content_layout.addSpacing(8)

        # Create cards for each answer
        for answer in data.answers:
            self._add_answer_card(answer)
            self.content_layout.addSpacing(8)

    def _add_answer_card(self, answer: AnswerDTO) -> None:
        """Create a custom card widget for a single answer choice."""
        answer_card = CardWidget()
        card_layout = QHBoxLayout(answer_card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(12)

        # Answer text
        answer_label = BodyLabel(answer.text)
        answer_label.setWordWrap(True)
        answer_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        card_layout.addWidget(answer_label, 1)  # Stretch to fill space

        # Right side: peer percentage and correctness icon
        right_layout = QHBoxLayout()
        right_layout.setSpacing(8)

        # Peer selection percentage (if available)
        if answer.peer_percentage is not None:
            peer_btn = PillPushButton(f"{answer.peer_percentage:.0f}%")
            peer_btn.setEnabled(False)  # Make it non-interactive (display only)
            right_layout.addWidget(peer_btn)

        # Correctness icon
        if answer.is_correct:
            icon = IconWidget(FluentIcon.ACCEPT)
            icon.setFixedSize(20, 20)
        else:
            icon = IconWidget(FluentIcon.CLOSE)
            icon.setFixedSize(20, 20)
        right_layout.addWidget(icon)

        card_layout.addLayout(right_layout)

        # Visual distinction for user's selected answer
        if answer.was_user_selected:
            # Add a colored border using theme accent color
            answer_card.setStyleSheet(
                "CardWidget { border: 2px solid palette(highlight); }"
            )

        self.content_layout.addWidget(answer_card)

    def _build_explanation_section(self, data: QuestionDetailDTO) -> None:
        """Build the Explanation section with educational objective and details."""
        # Section title
        section_title = TitleLabel("Explanation")
        self.content_layout.addWidget(section_title)
        self.content_layout.addSpacing(8)

        # Educational objective in a prominent InfoBar (if present)
        if data.educational_objective:
            # Create a card for the educational objective
            objective_card = CardWidget()
            objective_layout = QVBoxLayout(objective_card)
            objective_layout.setContentsMargins(16, 12, 16, 12)

            objective_title = SubtitleLabel("Educational Objective")
            objective_title.setStyleSheet("color: palette(highlight);")
            objective_layout.addWidget(objective_title)

            objective_text = BodyLabel(data.educational_objective)
            objective_text.setWordWrap(True)
            objective_text.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            objective_layout.addWidget(objective_text)

            self.content_layout.addWidget(objective_card)
            self.content_layout.addSpacing(8)

        # Key points (if present)
        if data.key_points:
            key_points_label = SubtitleLabel("Key Points")
            self.content_layout.addWidget(key_points_label)
            self.content_layout.addSpacing(4)

            for point in data.key_points:
                point_label = BodyLabel(f"• {point}")
                point_label.setWordWrap(True)
                point_label.setTextInteractionFlags(
                    Qt.TextInteractionFlag.TextSelectableByMouse
                )
                self.content_layout.addWidget(point_label)
                self.content_layout.addSpacing(4)

            self.content_layout.addSpacing(8)

        # Full explanation (if present)
        if data.full_explanation:
            explanation_label = SubtitleLabel("Detailed Explanation")
            self.content_layout.addWidget(explanation_label)
            self.content_layout.addSpacing(4)

            # Use TextEdit for longer text content
            explanation_text = QTextEdit()
            explanation_text.setPlainText(data.full_explanation)
            explanation_text.setReadOnly(True)
            explanation_text.setFrameShape(QFrame.Shape.NoFrame)
            # Set a reasonable height
            explanation_text.setMinimumHeight(100)
            explanation_text.setMaximumHeight(400)
            self.content_layout.addWidget(explanation_text)

    def show_placeholder(self) -> None:
        """Show a helpful message when no question is selected."""
        self.scroll_area.setVisible(False)
        self.placeholder_widget.setVisible(True)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        """Clear all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
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
        self.content_layout.setSpacing(8)  # 8-pt grid spacing
        self.content_layout.setContentsMargins(16, 16, 16, 16)

        self.scroll_area.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll_area)


