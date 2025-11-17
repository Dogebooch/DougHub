# Plan: Notebook Feature - Phase 2 Smooth Navigation

## 1. Overview

This plan covers "Phase 2: Smooth Navigation." Building on the skeleton from Phase 1, the goal is to make the notebook fully interactive by programmatically navigating the `QWebEngineView` to the correct note when a user selects a question. This phase ensures the user experience is seamless and reliable.

- **Goals for this Phase:**
  - Implement a mechanism to programmatically open a specific note in the Notesium view by its path.
  - Securely wire the question selection UI event to trigger this navigation.
  - Ensure new notes created by DougHub are immediately available in Notesium's index for navigation.
- **Non-Goals for this Phase:**
  - Syncing metadata (tags, etc.) from note frontmatter back to the database.
  - UI for note management beyond selection-driven navigation.

## 2. Context and Constraints

- **This plan builds directly on the components from Phase 1.**
- **Relevant Files & Modules:**
  - `src/doughub/ui/notebook_view.py`
  - `src/doughub/ui/main_window.py`
  - `src/doughub/ui/deck_browser_view.py`
- **Open Question: Notesium Navigation:** This plan assumes Notesium supports navigation via a URL query parameter (e.g., `?file=path/to/note.md`). If it requires a JavaScript call, the implementation of `NotebookView.open_note` will change, but the overall architecture will not.

## 3. Implementation Checkpoints

### Checkpoint 1: Implement the Navigation Mechanism

**Task:** Implement the core navigation logic in the `NotebookView`.

1.  **Edit `src/doughub/ui/notebook_view.py`:**
    - Implement the `open_note(self, note_path: str)` method.
    - This method will construct a `QUrl` with the appropriate query parameter (e.g., `http://127.0.0.1:8123/?file=...`) and use `self.web_view.load()` to navigate.

- **Zen MCP Integration:** `codereview` the `open_note` method to ensure safe URL construction.

### Checkpoint 2: Connect UI to Trigger Navigation

**Task:** Wire the UI events to the new navigation logic, ensuring the correct order of operations.

1.  **Edit `src/doughub/ui/deck_browser_view.py`:**
    - After the call to `repository.ensure_note_for_question()` in the selection handler, emit a new signal: `note_ready_for_navigation(note_path: str)`. This guarantees the file exists before navigation is attempted.
2.  **Edit `src/doughub/ui/main_window.py`:**
    - Connect the `deck_browser_view.note_ready_for_navigation` signal to the `notebook_view.open_note` slot.

- **Zen MCP Integration:** `testgen` for the `DeckBrowserView` to write an integration test that verifies the `note_ready_for_navigation` signal is emitted with the correct path after a selection.

### Checkpoint 3: Ensure Navigation Stability

**Task:** Confirm that Notesium's file-watching is sufficient for new notes to be indexed before navigation.

1.  **Analysis:** The synchronous nature of `ensure_note_for_question` followed by the `note_ready_for_navigation` signal should prevent race conditions. The primary risk is the delay in Notesium's file watcher.
2.  **Action:** No new code is required for this checkpoint. The focus is on validation. If testing reveals indexing delays, a temporary `time.sleep(0.1)` can be added before the signal is emitted in `deck_browser_view.py` as a pragmatic workaround.

- **Zen MCP Integration:** `debug` should be used if any race conditions or freezes are observed during stress testing.

## 4. Validation

- **Automated:** Run `ruff check .`, `mypy .`, and `pytest`. Add a new automated UI test that uses `runJavaScript` to query the DOM of the web view and assert that the correct note's title or ID is displayed after a selection is simulated.
- **Manual:**
  1.  **Sequence Test:** Select several different questions in a row and confirm the notebook view updates correctly for each one.
  2.  **Index Test:** Select a brand-new question. Verify the note is created and that the notebook view successfully navigates to it (does not show a "not found" error).
  3.  **Stress Test:** Rapidly click through 20+ questions. Verify the UI remains responsive and eventually settles on the last selected note.
