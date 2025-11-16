# Plan: PyQt6 Minimal UI Framework

## 1. Overview

This plan outlines the creation of a minimal, modern PyQt6 user interface for DougHub. The UI will provide a clean, efficient experience for browsing Anki decks and adding/editing cards, drawing inspiration from Brainscape's focused design. It will be built on the existing backend repository, ensuring a clean separation of concerns.

-   **Goal**: Implement a functional GUI for core deck and note management.
-   **Non-Goal**: Build a feature-complete replacement for the Anki desktop app. The focus is on a minimal, high-utility interface.

## 2. Context and Constraints

-   **Framework**: `PyQt6` (already in `pyproject.toml`).
-   **Backend**: The UI will interact exclusively with the `AnkiRepository` class located in `src/doughub/anki_client/repository.py`. No direct calls to the `api` or `transport` layers are permitted from the UI code.
-   **Project Structure**: All new UI code will reside in a new `src/doughub/ui/` directory.
-   **Styling**: The UI should be clean and minimal. We will use standard PyQt widgets for now, with an emphasis on clear layout and readability over custom styling.
-   **Concurrency**: UI will remain responsive by using Qt's signal/slot mechanism. Backend calls that might block will eventually need to be run in a separate thread, but for the initial implementation, we will assume the repository methods are fast enough.

## 3. Implementation Checkpoints (for Claude + Copilot)

### Checkpoint 1: UI Scaffolding and Main Window

-   **Task**: Create the main application window and the basic UI structure.
-   **Files to Create**:
    -   `src/doughub/ui/__init__.py` (can be empty).
    -   `src/doughub/ui/main_window.py`: Define a `MainWindow` class inheriting from `QMainWindow`. Set up a menu bar, a status bar, and a central `QStackedWidget`.
    -   `src/doughub/main.py`: Create the main entry point for the PyQt application. This will instantiate `QApplication` and `MainWindow`.
-   **Claude/Copilot Guidance**:
    -   Use Copilot to generate the boilerplate for a simple `QMainWindow` and `QApplication`.
    -   Claude should implement the main layout: a `QSplitter` with a placeholder for the deck list on the left and a `QStackedWidget` on the right. The stacked widget will hold the deck browser and card editor.

### Checkpoint 2: Deck List Panel

-   **Task**: Implement a panel to list all available Anki decks.
-   **Files to Create**:
    -   `src/doughub/ui/deck_list_panel.py`: Define a `DeckListPanel` widget (e.g., a `QWidget` containing a `QListWidget`).
-   **Implementation Details**:
    -   The panel will be initialized with an instance of `AnkiRepository`.
    -   On startup or refresh, it will call `repository.get_deck_names()` to populate the `QListWidget`.
    -   When a user selects a deck, the widget will emit a custom Qt signal, `deck_selected = pyqtSignal(str)`.
-   **Claude/Copilot Guidance**:
    -   In `main_window.py`, integrate the `DeckListPanel` into the left side of the splitter.
    -   Connect the `deck_selected` signal to a slot in `MainWindow` that will handle switching the view on the right.

### Checkpoint 3: Deck Browser View

-   **Task**: Display the notes of a selected deck in a table.
-   **Files to Create**:
    -   `src/doughub/ui/deck_browser_view.py`: Define a `DeckBrowserView` widget containing a `QTableView`.
-   **Implementation Details**:
    -   Create a simple `QAbstractTableModel` to display note data (e.g., Note ID, Fields).
    -   When the `deck_selected` signal is received by `MainWindow`, it will call `repository.find_notes_in_deck(deck_name)` and pass the resulting list of notes to the `DeckBrowserView` to update the model.
    -   Double-clicking a row in the table should emit a `note_selected = pyqtSignal(int)` with the note ID.
-   **Claude/Copilot Guidance**:
    -   Add the `DeckBrowserView` as the first widget in the `QStackedWidget` in `MainWindow`.
    -   Claude should focus on correctly implementing the `QAbstractTableModel` boilerplate (`rowCount`, `columnCount`, `data`).

### Checkpoint 4: Card Editor View

-   **Task**: Create a form to add and edit notes.
-   **Files to Create**:
    -   `src/doughub/ui/card_editor_view.py`: Define a `CardEditorView` widget.
-   **Implementation Details**:
    -   The view will have two modes: "add" and "edit".
    -   It will use `QComboBox` for Deck and Model selection, populated via `repository.get_deck_names()` and `repository.get_model_names()`.
    -   When a model is selected, the view will dynamically generate `QLineEdit` or `QTextEdit` widgets for each field by calling `repository.get_model_field_names(model_name)`.
    -   A "Save" button will trigger either `repository.add_note()` or `repository.update_note_fields()` based on the mode.
-   **Claude/Copilot Guidance**:
    -   Use a `QFormLayout` for a clean presentation of fields.
    -   Claude should implement the logic for dynamically creating the form based on model fields.
    -   Add the `CardEditorView` as the second widget in the `QStackedWidget`.

### Checkpoint 5: Final Integration

-   **Task**: Connect all components and handle UI state transitions.
-   **Files to Modify**:
    -   `src/doughub/ui/main_window.py`
-   **Implementation Details**:
    -   Connect the `DeckBrowserView`'s `note_selected` signal to a slot in `MainWindow` that switches the `QStackedWidget` to the `CardEditorView` and populates it with the note's data (`repository.get_note_info`).
    -   Add an "Add Note" button to the main window that switches to the `CardEditorView` in "add" mode.
    -   Use the `statusBar` to display feedback (e.g., "Note saved.", "Anki connection error.").

## 4. Zen MCP Integration

-   **`codereview`**: After each checkpoint, run `codereview` on the newly created/modified files in `src/doughub/ui/` to ensure they follow PyQt best practices and maintain separation from the backend.
-   **`testgen`**: After Checkpoint 4, use `testgen` to create unit tests for `CardEditorView`. The tests should mock the `AnkiRepository` dependency and verify that the form is generated correctly for a given model and that the correct repository methods are called on save.
-   **`precommit`**: Before finalizing the feature, run `precommit` to execute all validation steps (`ruff`, `mypy`, `pytest`).

## 5. Behavior Changes

-   This is a net-new feature. It adds a GUI entry point to the application but does not alter any existing backend or CLI behavior.
-   A new main entry point will be created in `src/doughub/main.py`. We may want to add a `[project.gui_scripts]` entry to `pyproject.toml` later.

## 6. End-user Experience

-   The user will launch the application and be presented with a list of their Anki decks.
-   Selecting a deck shows its cards in a table.
-   Double-clicking a card opens a form to edit it.
-   A prominent "Add Note" button allows the creation of new notes.
-   The status bar will provide clear, non-intrusive feedback on the status of operations (e.g., "Loading decks...", "Note updated successfully.", "Error: Could not connect to Anki.").

## 7. Validation

1.  **Static Analysis**: Run the following commands from the project root:
    -   `ruff check .`
    -   `mypy .`
2.  **Unit Tests**: Run the existing and new tests:
    -   `pytest`
3.  **Manual Validation**:
    -   Launch the UI via `python -m src.doughub.main`.
    -   Verify that the deck list populates correctly.
    -   Select a deck and confirm the card browser shows the correct notes.
    -   Double-click a note, make a change, save it, and verify the change in the Anki desktop application.
    -   Click "Add Note", select a deck and model, fill in the fields, save it, and verify the new note appears in Anki.
    -   Check that status bar messages appear as expected.
