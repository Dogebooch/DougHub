# Plan: Implement Tabbed UI with Question Detail View

## 1. Overview

This plan outlines a significant UI refactoring to introduce a top-level tabbed interface in the `MainWindow`. This change will separate the existing "Anki" functionality (deck browsing, card editing) from a new, forthcoming "Extracted Questions" area.

- **Goal:**
    - Refactor `MainWindow` to use a `QTabWidget` as the central widget.
    - Create two tabs: "Anki" and "Extracted Questions".
    - The "Anki" tab will contain the existing three-pane layout (Decks, Browser/Editor, Notebook).
    - The "Extracted Questions" tab will be a placeholder for future functionality.
    - Integrate the new `QuestionDetailView` into the "Anki" tab's middle pane.
- **Non-Goal:** This plan does not cover the implementation of the "Extracted Questions" view itself, which will be handled in a subsequent effort.

## 2. Context and Constraints

- **Framework:** PyQt6
- **Existing UI Structure:**
    - `src/doughub/ui/main_window.py`: The main application window (`MainWindow`), currently using a `QHBoxLayout` with a `QSplitter`.
- **New UI Structure:**
    - `MainWindow`'s central widget will become a `QTabWidget`.
    - The "Anki" tab will contain the `QSplitter` that holds the `DeckListPanel`, the middle `QStackedWidget`, and the `NotebookView`.
    - The "Extracted Questions" tab will contain a placeholder widget.

## 3. Implementation Checkpoints

### Checkpoint 1: Refactor `MainWindow` for Tabbed Interface

Modify `MainWindow` to use a `QTabWidget` as its main layout.

- **File to Modify:** `src/doughub/ui/main_window.py`
- **Action:**
    1. In `MainWindow._setup_ui`, create a `QTabWidget` and set it as the central widget of the `MainWindow`.
    2. Create a new `QWidget` to serve as the container for the "Anki" tab.
    3. Move the existing `QSplitter` and its contents (deck list, stacked widget, notebook view) into this new "Anki" container widget.
    4. Add the "Anki" container widget to the `QTabWidget` with the label "Anki".
    5. Create a simple `QWidget` placeholder for the "Extracted Questions" tab and add it to the `QTabWidget` with the label "Extracted Questions".

### Checkpoint 2: Create the `QuestionDetailView` Widget

Create the new file for the `QuestionDetailView` widget. This component will display question content.

- **File to Create:** `src/doughub/ui/question_detail_view.py`
- **Action:** Implement the `QuestionDetailView` class as a `QWidget` containing `QTextBrowser` widgets for the question, answers, and explanation, all within a `QScrollArea`.

```python
# src/doughub/ui/question_detail_view.py

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextBrowser,
    QScrollArea,
    QSizePolicy,
)

logger = logging.getLogger(__name__)

class QuestionDetailView(QWidget):
    """
    Read-only view for a single question, its answers, and explanation.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def set_question_html(self, html: str) -> None:
        self.question_view.setHtml(html or "")

    def set_answers_html(self, html: str) -> None:
        self.answers_view.setHtml(html or "")

    def set_explanation_html(self, html: str) -> None:
        self.explanation_view.setHtml(html or "")

    def clear(self) -> None:
        """Clears all views."""
        self.question_view.clear()
        self.answers_view.clear()
        self.explanation_view.clear()

    def _init_ui(self) -> None:
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

        # Question
        question_title = QLabel("Question", content)
        question_title.setFont(section_font)
        self.question_view = QTextBrowser(content)
        self.question_view.setOpenExternalLinks(True)
        content_layout.addWidget(question_title)
        content_layout.addWidget(self.question_view)

        # Answers
        answers_title = QLabel("Answers", content)
        answers_title.setFont(section_font)
        self.answers_view = QTextBrowser(content)
        self.answers_view.setOpenExternalLinks(True)
        content_layout.addWidget(answers_title)
        content_layout.addWidget(self.answers_view)

        # Explanation
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
```

### Checkpoint 3: Integrate `QuestionDetailView` into the "Anki" Tab

Incorporate the new view into the `QStackedWidget` within the "Anki" tab.

- **File to Modify:** `src/doughub/ui/main_window.py`
- **Action:**
    1.  Import `QuestionDetailView`.
    2.  In `MainWindow._setup_ui`, instantiate `self.question_detail_view = QuestionDetailView(self)`.
    3.  Add the new view to the `self.stacked_widget` that is now inside the "Anki" tab.

### Checkpoint 4: Wire Up the Selection Logic

Connect the `DeckBrowserView`'s selection signal to a slot in `MainWindow` to switch the view.

- **File to Modify:** `src/doughub/ui/deck_browser_view.py`
- **Action:**
    1.  Add a new signal: `note_review_selected = pyqtSignal(int)`.
    2.  Modify `_on_row_double_clicked` to emit this signal.

- **File to Modify:** `src/doughub/ui/main_window.py`
- **Action:**
    1.  In `MainWindow._connect_signals`, connect `deck_browser.note_review_selected` to a new `_on_note_review_selected` slot.
    2.  Implement `_on_note_review_selected` to fetch question data, populate the `question_detail_view`, and switch the `stacked_widget` to show it.

## 4. Zen MCP Integration

- **`codereview`:** After Checkpoint 1, run `codereview` on `main_window.py` to validate the new tabbed structure. After Checkpoint 4, run it on all modified files.
- **`testgen`:** Use `testgen` for the `QuestionDetailView` widget to ensure its content is set correctly.
- **`precommit`:** Run `precommit` before committing to ensure all checks pass.

## 5. Behavior Changes

- **New UI:** The application will now open with a tabbed interface. The default view will be the "Anki" tab.
- **New Tab:** A new, non-functional "Extracted Questions" tab will be present.
- **Interaction:** Double-clicking a note in the `DeckBrowserView` (in the "Anki" tab) will open the `QuestionDetailView` in the middle pane of that same tab.

## 6. End-user Experience

- Users can now switch between two primary contexts: "Anki" and "Extracted Questions".
- The "Anki" experience remains largely the same, but is now nested within a tab.
- The "Extracted Questions" tab signals a new area of functionality, even if not yet implemented.

## 7. Validation

1.  **Component Validation:**
    - Run the standalone harness for `QuestionDetailView`:
      ```bash
      python src/doughub/ui/question_detail_view.py
      ```
    - **Expected Result:** A window appears with formatted sample content.

2.  **Integration Validation:**
    - Run the main application: `python src/doughub/main.py`.
    - **Expected Result:** The main window opens with two tabs: "Anki" and "Extracted Questions". The "Anki" tab should be selected by default and show the familiar three-pane layout. The "Extracted Questions" tab should be empty or show a placeholder.
    - In the "Anki" tab, select a deck and double-click a note.
    - **Expected Result:** The middle pane of the "Anki" tab switches to the `QuestionDetailView` and displays the question.

3.  **Code Quality Validation:**
    - Run static analysis and tests:
      ```bash
      ruff check .
      mypy .
      pytest
      ```
    - **Expected Result:** All checks pass.