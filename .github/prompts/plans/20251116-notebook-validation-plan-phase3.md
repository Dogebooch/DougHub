# Validation Plan: Notebook Feature - Phase 3 Metadata Sync

## 1. Overview

This document provides a comprehensive validation plan for "Phase 3: Metadata Sync." The goal is to ensure that the one-way synchronization of metadata from a note's YAML frontmatter to the application's SQLite database is accurate, reliable, and robust.

- **Validation Goals:**
  - The frontmatter parser correctly handles various valid and invalid formats.
  - The sync job accurately updates the database based on note content.
  - The sync process is idempotent and tolerant of errors.
  - Data consistency between the filesystem and the database can be verified.

## 2. Validation Checkpoints

### Checkpoint 1: Frontmatter Parsing

- **What to Validate:**
  - The YAML frontmatter parser reliably handles expected formats and degrades gracefully on bad input.
- **Validation Steps:**
  1.  **Unit Tests:** Create unit tests for the parsing function with a variety of synthetic inputs:
      - A full, well-formed frontmatter block.
      - Frontmatter with missing optional keys (e.g., no `tags`).
      - Different data types (e.g., `tags` as a list vs. a single string).
      - Invalid YAML syntax (e.g., incorrect indentation, unclosed quotes).
      - Assert that valid cases are parsed correctly and invalid cases raise a specific, controlled error or are logged and skipped, but do not crash the parser.
- **Acceptance Criteria:**
  - The parser correctly extracts data from all expected frontmatter variations.
  - Malformed frontmatter is logged and ignored, not fatal to the overall sync process.

### Checkpoint 2: Sync Job Behavior

- **What to Validate:**
  - The sync job correctly finds all notes, extracts their metadata, and updates the database without causing regressions or duplicate data.
- **Validation Steps:**
  1.  **Initial Sync:**
      - Prepare a test folder with several notes containing valid frontmatter.
      - Run the sync job on a clean database.
      - Verify that the corresponding rows in the `questions` table are updated with the correct metadata (e.g., `tags`, `topic`).
  2.  **Idempotency:**
      - Run the sync job twice in a row without changing any note files.
      - Verify that the database state is identical after the second run as it was after the first.
  3.  **Partial Edits:**
      - Manually modify the frontmatter of one or two notes in the test set.
      - Re-run the sync job.
      - Verify that only the records for the modified notes were updated in the database.
  4.  **Error Handling:**
      - Introduce a corrupted note file (e.g., invalid YAML) into the test set.
      - Run the sync job and verify that it logs a warning for the corrupted file but continues to process all other valid notes.
      - Test with notes that have a `question_uid` that does not exist in the database; confirm they are logged and skipped.
- **Acceptance Criteria:**
  - The sync job is safe to run repeatedly.
  - The database state reliably reflects the content of the note frontmatter after a sync.
  - The job is resilient to bad data in individual files.

### Checkpoint 3: Data Consistency Checks

- **What to Validate:**
  - A diagnostic tool can verify that the database and filesystem are not out of sync.
- **Validation Steps:**
  1.  **Implement a Diagnostic Command:** Create a new CLI command or internal function (`check_notebook_integrity`).
  2.  **DB -> Filesystem Check:** The tool should iterate through all questions in the DB with a `note_path`. For each, it must verify that the file exists and that the `question_uid` inside its frontmatter matches the database record. It should report any mismatches.
  3.  **Filesystem -> DB Check:** The tool should iterate through all `.md` files in the notes directory, parse their `question_uid`, and verify that a corresponding question exists in the database. It should report any orphan note files.
  4.  **Test the Check:** Manually introduce inconsistencies (e.g., delete a note file, change a `question_uid` in a file) and run the integrity check to ensure it reports the errors correctly.
- **Acceptance Criteria:**
  - In normal operation, the integrity check passes without errors.
  - When inconsistencies are present, the tool provides clear, actionable reports.

## 3. Cross-Phase Regression Checks

- After implementing Phase 3, run the following end-to-end checks:
  - **Phase 1 Regression:** Verify that stub note creation still works for new questions.
  - **Phase 2 Regression:** Verify that selecting questions still triggers smooth navigation in the notebook pane.
  - **Sync and Navigate:** Manually edit a note's frontmatter, run the sync, and then navigate to that note. Confirm that both the synced data (visible elsewhere in the app, if applicable) and the navigation work correctly. The sync process should not interfere with the navigation mechanism.
