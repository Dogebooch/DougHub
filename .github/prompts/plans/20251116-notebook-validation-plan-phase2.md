# Validation Plan: Notebook Feature - Phase 2 Smooth Navigation

## 1. Overview

This document provides a comprehensive validation plan for "Phase 2: Smooth Navigation." The goal is to ensure that the programmatic navigation between a selected question in DougHub and its corresponding note in the Notesium view is seamless, reliable, and performant.

- **Validation Goals:**
  - The mechanism for opening a note (URL or JS) works correctly.
  - New notes created by DougHub are immediately indexed and findable by Notesium.
  - The navigation system is stable under rapid use and free of race conditions.

## 2. Validation Checkpoints

### Checkpoint 1: Note-Opening Mechanism

- **What to Validate:**
  - The chosen mechanism successfully focuses the target note in the Notesium UI.
- **Validation Steps:**
  1.  **Automated Navigation Test:**
      - Create a test that simulates a question selection.
      - After the navigation logic fires, use `QWebEngineView.page().runJavaScript()` to execute a script in the web view.
      - The script should read a unique identifier from the Notesium DOM (e.g., the content of a `<div id="note-title">` element).
      - Assert that the retrieved identifier matches the `question_uid` of the selected note.
  2.  **Manual Verification:**
      - Select several different questions in sequence.
      - Confirm visually that the notebook editor's content updates to the correct note each time.
  3.  **Nonexistent Note Path:**
      - Manually set a `note_path` in the database to a file that does not exist.
      - Select the corresponding question.
      - Verify that the application correctly detects the missing file, recreates it as a stub, and then successfully navigates to it.
- **Acceptance Criteria:**
  - After a question is selected, the correct note becomes active in the Notesium view.
  - The system gracefully handles and corrects missing note files before navigation.

### Checkpoint 2: New Notes Appearing in Notesium Index

- **What to Validate:**
  - A new `.md` file created by DougHub becomes searchable in Notesium without a server restart.
- **Validation Steps:**
  1.  **Basic Detection:**
      - Select a question that has no note, triggering stub creation.
      - Immediately use the search feature within the Notesium UI.
      - Verify that the new note is findable by its filename or `question_uid`.
  2.  **Graph Integration (if applicable):**
      - Manually edit the new stub note to include a link to another existing note (e.g., `[[some-other-note]]`).
      - Save the note within the Notesium editor.
      - Open the graph view in Notesium and confirm that the new link is rendered.
- **Acceptance Criteria:**
  - Notes created by DougHub are treated as first-class citizens by Notesium's indexer and are immediately available for search and linking.

### Checkpoint 3: Navigation Stability and Performance

- **What to Validate:**
  - Rapid navigation between notes does not cause the UI to freeze, crash, or lose synchronization.
- **Validation Steps:**
  1.  **Stress Test:**
      - In a test deck with 100+ questions, rapidly click through 20-30 different items.
      - Monitor the application for freezes or crashes.
      - Verify that the notebook pane remains responsive and eventually settles on the content of the last-selected question.
  2.  **Race Condition Check:**
      - The implementation ensures file creation is completed before the navigation signal is emitted.
      - Verify through logs and manual testing that there are no instances where Notesium attempts to open a note that doesn't exist yet.
- **Acceptance Criteria:**
  - The notebook pane remains responsive and correctly synchronized with the selected question, even under fast user input.

## 3. Cross-Phase Regression Checks

- After implementing Phase 2, run the following checks to ensure Phase 1 functionality is not broken:
  - **Startup:** Verify DougHub still starts correctly, launches Notesium, and displays the UI.
  - **Stub Creation:** Verify that selecting a brand-new question still correctly creates the `.md` file on the filesystem and updates the database `note_path`.
  - **Error Handling:** Verify that failure cases from Phase 1 (e.g., port in use) are still handled gracefully.
