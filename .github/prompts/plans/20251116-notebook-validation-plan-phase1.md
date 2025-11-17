# Validation Plan: Notebook Feature - Phase 1 Skeleton Integration

## 1. Overview

This document provides a comprehensive validation plan for "Phase 1: Skeleton Integration" of the notebook feature. The goal is to ensure that the foundational components are implemented correctly and robustly. This includes testing the configuration, database schema changes, subprocess management, UI embedding, and stub note creation.

- **Validation Goals:**
  - `notes_root` config is correctly loaded and used.
  - SQLite schema migration is safe and effective.
  - The Notesium subprocess is launched and managed reliably.
  - The embedded web view displays the Notesium UI correctly.
  - Stub notes are created idempotently on question selection.

## 2. Validation Checkpoints

This plan is broken down into checkpoints corresponding to the key features of Phase 1.

### Checkpoint 1: Config and Notes Root

- **What to Validate:**
  - Config values are read from a single source of truth.
  - The application behaves correctly when the notes path is missing, invalid, or read-only.
- **Validation Steps:**
  1.  **Unit Tests:**
      - Test the config loader with a valid `notes_root` path.
      - Test the fallback to a default path when the config entry is missing.
      - Test that an invalid path (e.g., with forbidden characters) raises a specific error.
  2.  **Filesystem Validation:**
      - On a fresh start, verify that DougHub creates the `notes_root` directory and its subdirectories (`notes/`, `media/`).
      - Test behavior when permissions are insufficient to create the directory; verify a clear error is shown and the notebook pane is disabled gracefully.
  3.  **Edge Cases:**
      - Test `notes_root` paths containing spaces and non-ASCII characters.
      - Update the config to point to a new location and confirm DougHub uses the new path.
- **Acceptance Criteria:**
  - A fresh run with a valid config creates the notes directory.
  - An invalid or inaccessible path results in a clear, non-fatal error message.

### Checkpoint 2: SQLite Schema

- **What to Validate:**
  - The Alembic migration adds the `note_path` field safely without data loss.
  - Note paths can be assigned to new and existing questions.
- **Validation Steps:**
  1.  **Migration Dry Runs:** Apply the migration to a blank test DB and a populated test DB. Verify no data is lost and the new `note_path` column exists with `NULL` defaults.
  2.  **Integration Tests:**
      - Create a new question and verify `note_path` is initially `NULL`.
      - Simulate note creation, set the `note_path`, save, and re-fetch the question to ensure the path is persisted correctly.
  3.  **Backward Compatibility:** Run the new application version against a database from before the migration. Verify the app starts, all questions are accessible, and new notes can be created for old questions.
- **Acceptance Criteria:**
  - The schema migration is repeatable and causes no data loss.
  - The application can correctly read and write to the `note_path` field.

### Checkpoint 3: Notesium Launcher and Lifecycle

- **What to Validate:**
  - DougHub can reliably start, health-check, and stop the Notesium subprocess.
  - Failure scenarios (port in use, missing binary) are handled gracefully.
- **Validation Steps:**
  1.  **Happy Path:** Start DougHub and verify the Notesium process is running (via logs or task manager). Confirm its health endpoint (`http://127.0.0.1:<port>/`) returns HTTP 200.
  2.  **Port in Use:** Manually start a server on the Notesium port, then launch DougHub. Verify a specific "port in use" error is shown in the notebook pane and the app does not crash.
  3.  **Missing Binary:** Misconfigure the path to the Notesium executable. Verify a "Notesium not found" error is shown and the rest of the app remains usable.
  4.  **Shutdown:** Close DougHub and verify the Notesium subprocess is terminated.
- **Acceptance Criteria:**
  - The notebook pane is available within seconds of a normal app start.
  - All error conditions result in clear, non-fatal error messages.

### Checkpoint 4: Embedded Web View

- **What to Validate:**
  - The `QWebEngineView` correctly renders the Notesium UI and remains responsive.
- **Validation Steps:**
  1.  **Manual UI Check:** Start DougHub and confirm the Notesium UI (search, editor) is visible and interactive in the right-hand pane.
  2.  **Resizing/Docking:** Resize the main window and splitter. If using a `QDockWidget`, undock and redock the pane. Confirm the web view resizes and functions correctly.
  3.  **Reload:** Test a "Reload Notebook" action (if implemented) and confirm the UI reloads successfully.
- **Acceptance Criteria:**
  - The embedded view is as responsive and functional as Notesium in a standalone browser.
  - The view does not crash or go blank during typical window management actions.

### Checkpoint 5: Stub Note Creation

- **What to Validate:**
  - Selecting a question creates a correct, idempotent stub note file and updates the database.
- **Validation Steps:**
  1.  **First Selection:** Select a question with no `note_path`. Verify a `notes/<question_uid>.md` file is created with a valid YAML frontmatter block (containing `question_uid`, etc.). Verify the `note_path` is updated in the database.
  2.  **Idempotency:** Select the same question multiple times. Confirm the file is not recreated and any manual edits to the note body are preserved.
  3.  **Edge Cases:** Test with `question_uid`s that may be unsafe for filenames to ensure they are handled correctly. Test that if the `notes_root` is deleted, it is recreated before the stub note is created.
- **Acceptance Criteria:**
  - Every question can have exactly one note created on first selection.
  - Repeated selections are safe and do not cause data loss.
