# Plan: Notebook Feature - Phase 3 Metadata Sync

## 1. Overview

This plan covers "Phase 3: Metadata Sync." With the core notebook functionality and navigation in place, this phase focuses on creating a one-way data sync from the note files back to the application's database. This allows metadata edited or stored in a note's frontmatter (e.g., tags, state) to be queryable and usable by the main DougHub application, preparing for future AI and advanced features.

- **Goals for this Phase:**
  - Implement a sync job that reads the YAML frontmatter from all `.md` files in the notes directory.
  - Safely parse the frontmatter to extract relevant metadata.
  - Update the corresponding records in the SQLite database with this metadata.
- **Non-Goals for this Phase:**
  - A real-time, two-way sync. The sync is one-way (file -> database) and can be triggered periodically or at startup.
  - A UI for editing metadata within the main DougHub application.

## 2. Context and Constraints

- **This plan builds on the components from Phases 1 and 2.**
- **Relevant Files & Modules:**
  - `src/doughub/persistence/repository.py`
  - `src/doughub/main.py`
- **New Components to be Created:**
  - **Metadata Sync Service:** `src/doughub/notebook/sync.py`
- **Dependencies:**
  - This phase will likely require adding `PyYAML` or a similar library to parse frontmatter. This should be added to `pyproject.toml`.
- **Constraints:**
  - The sync process must be robust against malformed YAML or missing files.
  - The database updates should be efficient and transactional.

## 3. Implementation Checkpoints

### Checkpoint 1: Create the Metadata Sync Service

**Task:** Implement the core logic for scanning and parsing notes.

1.  **Add Dependency:** Add `PyYAML` to the project's dependencies in `pyproject.toml`.
2.  **Create `src/doughub/notebook/sync.py`:**
    - Implement a function `scan_and_parse_notes(notes_dir: Path) -> Iterator[dict]`.
    - **Logic:**
        1.  Walk the `notes_dir` and find all `.md` files.
        2.  For each file, open it and extract the YAML frontmatter block.
        3.  Use `yaml.safe_load()` to parse the frontmatter into a dictionary.
        4.  Include the `question_uid` (from the filename or frontmatter) in the dictionary.
        5.  `yield` the dictionary for each successfully parsed note.
        6.  Handle errors gracefully (e.g., parsing errors, file read errors) by logging them and continuing.

- **Zen MCP Integration:** `testgen` for `scan_and_parse_notes`, using a temporary directory with sample valid and malformed note files to test parsing and error handling.

### Checkpoint 2: Implement Database Update Logic

**Task:** Create the persistence layer method to save the parsed metadata.

1.  **Edit `src/doughub/models.py`:**
    - Add new fields to the `Question` model to store the synced metadata. For example: `tags: Mapped[str | None]` or `state: Mapped[str | None]`.
2.  **Generate Alembic Migration:** Create and verify a new migration to add these columns to the database.
3.  **Edit `src/doughub/persistence/repository.py`:**
    - Implement a new method `update_question_from_metadata(self, metadata: dict)`.
    - **Logic:**
        1.  Extract the `question_uid` from the metadata dictionary.
        2.  Find the corresponding `Question` in the database.
        3.  Update the question's fields (e.g., `tags`, `state`) with values from the metadata.
        4.  This method should operate within a transaction.

- **Zen MCP Integration:** `codereview` the model changes and the new repository method. `testgen` for `update_question_from_metadata` using a mock database session.

### Checkpoint 3: Trigger the Sync Process

**Task:** Run the sync job when the application starts.

1.  **Edit `src/doughub/main.py`:**
    - In the main application startup sequence (after the database is initialized), call the sync logic.
    - **Logic:**
        1.  Instantiate the repository.
        2.  Call `sync.scan_and_parse_notes()` to get an iterator of metadata.
        3.  Loop through the metadata and call `repository.update_question_from_metadata()` for each item.
        4.  Commit the transaction once all notes have been processed.
        5.  This should be done in a way that doesn't block the UI from appearing for too long, potentially on a background thread (`QThread`) if the number of notes is large. For v1, a simple startup job is sufficient.

- **Zen MCP Integration:** `analyze` the startup sequence to ensure the sync job doesn't introduce significant launch delays.

## 4. Validation

- **Automated:** Run `ruff check .`, `mypy .`, and `pytest`.
- **Manual:**
  1.  **Add Metadata:** Manually edit a note file and add a `tags: ["new-tag"]` line to its frontmatter.
  2.  **Restart and Verify:** Restart the DougHub application.
  3.  **Check Database:** Use a database browser to inspect the `questions` table. Verify that the `tags` column for the corresponding question has been updated to `"['new-tag']"` or similar.
  4.  **Malformed File Test:** Introduce a syntax error into a note's YAML frontmatter (e.g., an unclosed quote).
  5.  **Restart and Verify:** Restart the app. Verify that the app starts without crashing and that an error message is logged regarding the malformed file. Other valid notes should still be synced correctly.
