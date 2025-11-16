# Plan: Validation Strategy for Persistence Layer

## 1. Overview

This plan details the implementation of a comprehensive validation strategy for the new SQLite-based persistence layer. The goal is to ensure the implementation is correct, robust, and reliable through a multi-layered approach including unit tests, integration tests, data integrity scripts, and manual inspection tools.

- **Goals:**
  - Implement unit tests for the persistence repository in isolation.
  - Implement integration tests for the extraction importer, verifying file system and database interactions.
  - **Validate the automatic persistence of log records to the database.**
  - Create standalone scripts for periodic data integrity checks and performance validation.
  - Add CLI commands for manual data inspection and QA.
- **Non-Goals:**
  - This plan does not cover UI-level testing.
  - Performance tuning is out of scope; the goal is to establish a baseline, not optimize.

## 2. Context and Constraints

- **Relevant Frameworks/Libraries:**
  - **Pytest:** The testing framework. Fixtures will be heavily used for setting up test states (e.g., in-memory DB, synthetic file structures).
- **Files to Modify:**
  - `tests/test_persistence.py`: This will contain the core unit and integration tests.
  - `tests/conftest.py`: To define shared pytest fixtures for the test database and synthetic data.
  - `src/doughub/cli.py`: To add new inspection commands.
  - `src/doughub/models.py`: To add the `Log` model.
- **Files/Modules to Create:**
  - `tests/test_logging.py`: To test the persistent logging handler.
  - `scripts/check_db_integrity.py`: A read-only script to validate the integrity of the production database.
  - `scripts/load_test_db.py`: A script to generate a large volume of synthetic data for basic performance checks.
  - `tests/fixtures/synthetic_extractions/`: A directory structure to be created by a fixture, containing sample HTML, JSON, and image files for importer tests.
- **Constraints:**
  - Tests must be isolated and not interfere with the production `doughub.db` file.
  - Integrity scripts should be read-only to prevent accidental data modification.

## 3. Implementation Checkpoints (for Claude + Copilot)

**Checkpoint 1: Pytest Fixture Setup**
- **Task:** Define shared `pytest` fixtures in `tests/conftest.py` to support the test suite.
- **File:** `tests/conftest.py`
- **Fixtures to create:**
  1.  `test_db_session`: Sets up an in-memory SQLite database, creates the schema using the defined models, yields a SQLAlchemy session for the test to use, and tears everything down afterward.
  2.  `synthetic_extraction_dir`: Creates a temporary directory with a structure mimicking `extractions/` (e.g., `peerprep/q1/q1.html`, `mksap/q2/q2.json`). It should create a few valid items, one with missing media, and one with malformed JSON to test various scenarios. It should yield the path to this temporary directory.
- **Copilot Assist:** Use Copilot to generate the boilerplate for creating temporary directories and files with `pathlib` and the `tmp_path` fixture.

**Checkpoint 2: Implement Unit Tests for the Repository**
- **Task:** In `tests/test_persistence.py`, write unit tests for the `QuestionRepository` to verify its logic in isolation. These tests should only use the `test_db_session` fixture.
- **File:** `tests/test_persistence.py`
- **Test Groups:**
  - **Source CRUD:** Test creating, retrieving, and handling duplicate sources.
  - **Question Lifecycle:** Test creating a question, retrieving it, updating its status, and verifying timestamps.
  - **Idempotency:** Test that adding a question with the same `(source_id, source_question_key)` does not create a duplicate.
  - **Media Attachment:** Test adding multiple media records to a question and retrieving them correctly.
- **Copilot Assist:** Use Copilot to quickly generate test function skeletons and basic `assert` statements based on the function signatures in the repository.

**Checkpoint 3: Implement Tests for Persistent Logging**
- **Task:** Create tests to verify that log messages sent via Python's standard `logging` library are correctly persisted to the database.
- **File:** `tests/test_logging.py`
- **Test Scenarios:**
  1.  Configure the logging system to use the persistent handler with the `test_db_session`.
  2.  Emit a log message using `logging.info("my test message")`.
  3.  Query the `Log` table and assert that a record was created with the correct level, message, and timestamp.
  4.  Test that log messages below the configured threshold (e.g., `DEBUG`) are not persisted.
- **Copilot Assist:** Use Copilot to help with configuring the logger within the test and for querying the database to verify the results.

**Checkpoint 4: Implement Integration Tests for the Importer**
- **Task:** In `tests/test_persistence.py`, write integration tests for the ingestion logic. These tests will use both the `test_db_session` and `synthetic_extraction_dir` fixtures.
- **File:** `tests/test_persistence.py`
- **Test Scenarios:**
  1.  **Happy Path:** Run the importer on the synthetic directory and assert that the correct number of `Source`, `Question`, and `Media` rows are created. Verify that file contents match and media files were correctly moved.
  2.  **Idempotency:** Run the importer a second time and assert that no new rows are created.
  3.  **Error Handling:** Run the importer on the malformed parts of the synthetic directory and assert that it logs errors correctly (both to stderr/stdout and the persistent log) and does not create partial/invalid database entries.
- **Copilot Assist:** This is a good place to use Copilot to help structure the test, especially for asserting file existence and content matching.

**Checkpoint 5: Create Data Integrity and Performance Scripts**
- **Task:** Implement standalone scripts for database maintenance and validation.
- **Files to Create:**
  - `scripts/check_db_integrity.py`: This script connects to the database specified in `config.py` and runs read-only checks (e.g., verifies all `Media.relative_path` entries point to existing files, checks for orphaned questions). It should print a summary report.
  - `scripts/load_test_db.py`: This script generates and inserts a large number (e.g., 10,000) of synthetic `Question` and `Media` records into a specified database file to provide a simple load for performance evaluation.
- **Copilot Assist:** Use Copilot to generate the argument parsing boilerplate (`argparse` or `typer`) and the main loops for iterating over database records.

**Checkpoint 6: Add Manual Inspection CLI Commands**
- **Task:** Extend the existing CLI to include commands for inspecting the database.
- **File:** `src/doughub/cli.py`
- **Commands to add:**
  - `doughub db show-question --id <question_id>`: Displays a formatted summary of a question, including its source, key, status, and a list of associated media paths.
  - `doughub db source-summary`: Lists all sources and the number of questions associated with each.
- **Copilot Assist:** Use Copilot to generate the `typer` command functions and the associated calls to the `QuestionRepository`.

## 4. Zen MCP Integration

- **During Checkpoint 2, 3, & 4 (Testing):**
  - Use `testgen` on `src/doughub/persistence/repository.py`, `src/doughub/ingestion.py`, and the logging handler to generate a baseline set of test cases.
  - After implementing the tests, run `codereview` on `tests/test_persistence.py` and `tests/test_logging.py` to check for test quality, coverage, and best practices.
- **During Checkpoint 5 (Scripts):**
  - Run `codereview` on `scripts/check_db_integrity.py` to ensure it is safe (read-only) and provides clear output.
- **Final Validation:**
  - Run `precommit` to execute all static analysis and the full test suite before committing the validation code.

## 5. Behavior Changes

- This plan introduces new development and operational tools. There are no changes to the core application's behavior.
- A new `Log` table will be added to the database schema.
- New CLI commands under `doughub db` will be added.

## 6. End-user Experience

- The new CLI commands provide a direct way for the developer/user to interact with and verify the contents of the database. The output should be formatted for readability.
- The integrity script provides peace of mind and a tool for diagnosing potential issues with the data. Its summary report should be clear and actionable.

## 7. Validation

The successful implementation of this plan is validated by the successful execution of the tools it creates.
1.  **Run All Tests:**
    - `poetry run pytest tests/test_persistence.py`
    - `poetry run pytest tests/test_logging.py`
2.  **Run Static Analysis:**
    - `poetry run ruff check .`
    - `poetry run mypy .`
3.  **Execute Integrity Script:**
    - First, run the real importer to populate the database.
    - Then, run `poetry run python scripts/check_db_integrity.py`. Verify the output shows no errors.
4.  **Test Manual Inspection CLI:**
    - `poetry run doughub db source-summary`
    - `poetry run doughub db show-question --id 1` (or another valid ID)
    - Verify the output is well-formatted and accurate.
