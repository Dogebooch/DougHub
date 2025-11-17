# Plan: Notebook Feature - Phase 1 Skeleton Integration

## 1. Overview

This plan covers the "Skeleton Integration" (Phase 1) for the new notebook feature. The goal is to establish the core infrastructure: configuring the notes directory, updating the database, managing the Notesium server as a subprocess, setting up the UI with an embedded web view, and implementing basic stub note creation.

- **Goals for this Phase:**
  - Add and load a `notes_root` configuration.
  - Add a `note_path` field to the `Question` model via a database migration.
  - Reliably launch, health-check, and shut down a Notesium subprocess.
  - Embed a `QWebEngineView` in the UI that loads the Notesium interface.
  - Create empty stub note files on question selection and link them in the database.
- **Non-Goals for this Phase:**
  - Automatic navigation to the created note within the web view.
  - Syncing metadata from the note file back to the database.

## 2. Context and Constraints

- **Relevant Files & Modules:**
  - **Configuration:** `src/doughub/config.py`
  - **Data Models:** `src/doughub/models.py`
  - **Persistence:** `src/doughub/persistence/repository.py`
  - **Application Lifecycle:** `src/doughub/main.py`
  - **UI:** `src/doughub/ui/main_window.py`, `src/doughub/ui/deck_browser_view.py`
- **New Components to be Created:**
  - **Notebook Subprocess Manager:** `src/doughub/notebook/manager.py`
  - **Notebook UI View:** `src/doughub/ui/notebook_view.py`
- **Constraints:**
  - The feature must degrade gracefully if the Notesium subprocess fails to start or the notes directory is inaccessible. The main application must remain functional.

## 3. Implementation Checkpoints

### Checkpoint 1: Configuration and Database Schema

**Task:** Configure the notes directory and update the database model.

1.  **Edit `src/doughub/config.py`:** Add a `NOTES_DIR` configuration, defaulting to a path within the user's application data directory. Also add `NOTESIUM_PORT`.
2.  **Edit `src/doughub/models.py`:** Add `note_path: Mapped[str | None] = mapped_column(String, nullable=True)` to the `Question` model.
3.  **Generate Alembic Migration:** Run `alembic revision --autogenerate -m "Add note_path to Question model"` and verify the generated script.

- **Zen MCP Integration:** `codereview` the model change and migration script. `testgen` for the config loading logic.

### Checkpoint 2: Notesium Subprocess Management

**Task:** Create a manager to handle the Notesium server lifecycle.

1.  **Create `src/doughub/notebook/manager.py`:** Implement a `NotesiumManager` class with `start()` and `stop()` methods. The `start()` method should perform a health check and handle failures (e.g., port in use).
2.  **Edit `src/doughub/main.py`:** Instantiate and use the `NotesiumManager` during application startup and shutdown.

- **Zen MCP Integration:** `testgen` for `NotesiumManager`, mocking `subprocess` and network calls to test success and failure scenarios.

### Checkpoint 3: UI Skeleton Integration

**Task:** Restructure the main window to include the web-based notebook pane.

1.  **Create `src/doughub/ui/notebook_view.py`:** Implement a `NotebookView(QWidget)` containing a `QWebEngineView`. Add methods to load a URL or display an error message.
2.  **Edit `src/doughub/ui/main_window.py`:** Use a `QSplitter` to add the `NotebookView` to the right of the existing question browser. Load the Notesium URL or show an error based on the `NotesiumManager`'s status.

- **Zen MCP Integration:** `codereview` the UI changes for proper layout and error handling.

### Checkpoint 4: Stub Note Creation

**Task:** Implement the logic to create a note file when a user selects a question.

1.  **Edit `src/doughub/persistence/repository.py`:** Create an idempotent method `ensure_note_for_question(self, question_uid: str)`. This method will create the stub `.md` file with YAML frontmatter if it doesn't exist and update the `note_path` in the database.
2.  **Edit `src/doughub/ui/deck_browser_view.py`:** In the question selection handler, call the new repository method.

- **Zen MCP Integration:** `testgen` for `ensure_note_for_question` to verify file creation and database updates.

## 4. Validation

- **Automated:** Run `ruff check .`, `mypy .`, and `pytest`.
- **Manual:**
  1. Verify the `notes` directory is created on first launch.
  2. Verify the UI shows the splitter with the Notesium view.
  3. Test graceful failure by blocking the Notesium port.
  4. Select a question and verify the `.md` file is created in the `notes` directory and the `note_path` is set in the database.
  5. Verify selecting the same question again does not cause an error.
