"""Question detail view for DougHub UI."""

import logging

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class QuestionDetailView(QWidget):
    """Read-only view for a single question, its answers, and explanation.

    This view displays formatted HTML content for reviewing questions without
    editing capabilities. It uses a scrollable layout with three distinct sections:
    question, answers, and explanation.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the question detail view.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._init_ui()

    def set_question_html(self, html: str) -> None:
        """Set the HTML content for the question section.

        Args:
            html: HTML string to display in the question section.
        """
        self.question_view.setHtml(html or "")

    def set_answers_html(self, html: str) -> None:
        """Set the HTML content for the answers section.

        Args:
            html: HTML string to display in the answers section.
        """
        self.answers_view.setHtml(html or "")

    def set_explanation_html(self, html: str) -> None:
        """Set the HTML content for the explanation section.

        Args:
            html: HTML string to display in the explanation section.
        """
        self.explanation_view.setHtml(html or "")

    def clear(self) -> None:
        """Clear all views, removing all content."""
        self.question_view.clear()
        self.answers_view.clear()
        self.explanation_view.clear()

    def _init_ui(self) -> None:
        """Set up the UI components with scrollable layout."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        root_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        section_font = QFont()
        section_font.setPointSize(14)
        section_font.setWeight(QFont.Weight.DemiBold)

        # Question section
        question_title = QLabel("Question", content)
        question_title.setFont(section_font)
        self.question_view = QTextBrowser(content)
        self.question_view.setOpenExternalLinks(True)
        content_layout.addWidget(question_title)
        content_layout.addWidget(self.question_view)

        # Answers section
        answers_title = QLabel("Answers", content)
        answers_title.setFont(section_font)
        self.answers_view = QTextBrowser(content)
        self.answers_view.setOpenExternalLinks(True)
        content_layout.addWidget(answers_title)
        content_layout.addWidget(self.answers_view)

        # Explanation section
        explanation_title = QLabel("Explanation", content)
        explanation_title.setFont(section_font)
        self.explanation_view = QTextBrowser(content)
        self.explanation_view.setOpenExternalLinks(True)
        content_layout.addWidget(explanation_title)
        content_layout.addWidget(self.explanation_view)

        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    w = QuestionDetailView()
    w.resize(900, 700)
    w.setWindowTitle("Question Detail View - Validation")

    sample_question = """
    <h3>65-year-old man with exertional chest pain</h3>
    <p>A 65-year-old man presents with exertional chest discomfort
    that resolves with rest. Which of the following is the most
    appropriate next step in management?</p>
    """

    sample_answers = """
    <ol>
      <li>Begin low-dose aspirin only</li>
      <li>Start high-intensity statin therapy</li>
      <li>Order an exercise treadmill test</li>
      <li>Schedule coronary angiography</li>
    </ol>
    """

    sample_explanation = """
    <p>The presentation is consistent with stable angina. Initial
    evaluation typically includes noninvasive stress testing in a
    patient with interpretable ECG and adequate functional capacity.</p>
    """

    w.set_question_html(sample_question)
    w.set_answers_html(sample_answers)
    w.set_explanation_html(sample_explanation)

    w.show()
    sys.exit(app.exec())
