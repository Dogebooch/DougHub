# Plan: SQLite Persistence Layer for Question Extractions

## 1. Overview

This plan outlines the implementation of a single-user, single-machine SQLite persistence layer for managing question extractions from multiple sources (e.g., Peerprep, MKSAP). The goal is to create a centralized, authoritative database for question and media metadata, treating the filesystem as an asset store. This will replace direct filesystem reads and provide a stable foundation for future features.

- **Goals:**
  - Establish a robust, single-file database for question data.
  - Define clear data models for `Source`, `Question`, and `Media`.
  - Create an idempotent ingestion process to import existing extractions from the `/extractions` directory.
  - Abstract database operations through a repository pattern.
- **Non-Goals:**
  - This is not a multi-user or server-based solution.
  - The initial implementation will not include complex UI for managing the data.
  - Full-text search or advanced querying is out of scope for this initial phase.

## 2. Context and Constraints

- **Relevant Frameworks/Libraries:**
  - **SQLAlchemy:** Will be used as the ORM. It needs to be added as a project dependency.
  - **Alembic:** Will be used for schema migrations. It needs to be added as a project dependency.
  - **SQLite:** The backend database engine.
- **Relevant Files/Modules:**
  - `pyproject.toml`: To add `sqlalchemy` and `alembic`.
  - `src/doughub/config.py`: To add database configuration (e.g., DB file path).
  - `src/doughub/models.py`: To define the SQLAlchemy data models.
- **Files/Modules to Create:**
  - `src/doughub/persistence/__init__.py`: To mark the directory as a package.
  - `src/doughub/persistence/repository.py`: To house the `QuestionRepository` class that encapsulates all database interactions (CRUD operations).
  - `src/doughub/ingestion.py`: A script or module responsible for scanning the `extractions/` directory and populating the database.
  - `tests/test_persistence.py`: Unit and integration tests for the models, repository, and ingestion logic.
  - `alembic/`: Directory for migration scripts, to be managed by Alembic.
- **Constraints:**
  - The solution must be self-contained within the project and work on a single machine without a separate database server.
  - The database schema should be evolvable. Using Alembic for migrations is required.

## 3. Implementation Checkpoints (for Claude + Copilot)

**Checkpoint 1: Setup Dependencies and Configuration**
- **Task:** Add `sqlalchemy` and `alembic` to the `[project.dependencies]` section in `pyproject.toml`.
- **File:** `pyproject.toml`
- **Task:** Initialize Alembic for migration management by running `poetry run alembic init alembic`.
- **Task:** In `src/doughub/config.py`, add a configuration variable for the SQLite database path, e.g., `DATABASE_URL = "sqlite:///doughub.db"`.
- **Copilot Assist:** Use Copilot to generate the basic configuration entry.

**Checkpoint 2: Define Core Data Models**
- **Task:** In `src/doughub/models.py`, define the SQLAlchemy models for `Source`, `Question`, and `Media` as described in the high-level plan. Use SQLAlchemy's Declarative Base.
- **File:** `src/doughub/models.py`
- **Details:**
  - `Source`: `source_id` (PK), `name` (unique), `description`.
  - `Question`: `question_id` (PK), `source_id` (FK to Source), `source_question_key` (string, for idempotency), `raw_html`, `raw_metadata_json`, `status`, `extraction_path`, `created_at`, `updated_at`. Create a unique constraint on `(source_id, source_question_key)`.
  - `Media`: `media_id` (PK), `question_id` (FK to Question), `media_role`, `media_type`, `mime_type`, `relative_path`.
- **Copilot Assist:** After defining the first model (`Source`), use Copilot to accelerate the creation of `Question` and `Media`, paying close attention to column types, foreign keys, and constraints.

**Checkpoint 3: Implement the Persistence Repository**
- **Task:** Create the `QuestionRepository` class in the new file `src/doughub/persistence/repository.py`. This class should handle the database session and provide methods for creating, retrieving, and updating questions and media.
- **File:** `src/doughub/persistence/repository.py`
- **Methods to implement:**
  - `__init__(self, session)`: Takes a SQLAlchemy session.
  - `get_or_create_source(self, name: str) -> Source`: Finds a source by name or creates it.
  - `add_question(self, question_data: dict) -> Question`: Adds a new question, ensuring idempotency using `source_question_key`.
  - `add_media_to_question(self, question_id: int, media_data: dict) -> Media`: Adds a media file associated with a question.
- **Copilot Assist:** Use Copilot to generate the boilerplate for the class methods, but manually verify the SQLAlchemy queries for correctness.

**Checkpoint 4: Build the Ingestion Logic**
- **Task:** In `src/doughub/ingestion.py`, create a function `ingest_extractions(session)`. This function will:
  1. Scan the `extractions/` directory.
  2. For each found question, determine its source from the directory structure.
  3. Compute the `source_question_key`.
  4. Use the `QuestionRepository` to add the question and its associated media to the database.
  5. Move media files to a canonical `media_root/` directory.
- **File:** `src/doughub/ingestion.py`
- **Copilot Assist:** This is a complex task. Use Copilot to help with file system operations (`os.walk` or `pathlib.glob`) and structuring the loops, but the core logic of calling the repository should be carefully crafted.

**Checkpoint 5: Write Unit and Integration Tests**
- **Task:** In `tests/test_persistence.py`, write tests for the functionality created.
- **File:** `tests/test_persistence.py`
- **Test cases:**
  - **Repository:** Test that `get_or_create_source` is idempotent. Test that `add_question` correctly creates a question and that adding the same one again does not create a duplicate.
  - **Ingestion:** Create a fake directory structure under `tests/fixtures/` mimicking the `extractions/` layout. Run the ingestion logic on it and assert that the correct number of questions and media records are created in a test database.
- **Copilot Assist:** Use Copilot to generate test function skeletons and basic assertions.

## 4. Zen MCP Integration

- **After Checkpoint 2 (Models):**
  - Run `codereview` on `src/doughub/models.py` to check for SQLAlchemy best practices and correct model definitions.
- **After Checkpoint 3 (Repository):**
  - Use `testgen` on `src/doughub/persistence/repository.py` to generate initial test cases for the repository methods.
  - Run `codereview` on both the repository and the generated tests to ensure correctness and completeness.
- **After Checkpoint 4 (Ingestion):**
  - If the ingestion script is complex or fails unexpectedly, use `debug` to step through its execution with a sample directory.
- **Final Validation:**
  - Before committing the final feature, run `precommit` to execute all configured static analysis, linting, and test suites.

## 5. Behavior Changes

- This feature is primarily additive. It introduces a new persistence backend.
- Existing code that might read from the `extractions/` directory directly will become obsolete and should be refactored in subsequent tasks to use the new `QuestionRepository`. This plan does not include that refactoring.
- A new file, `doughub.db`, will be created in the project root (or configured location). This file should be added to `.gitignore`.

## 6. End-user Experience

- As a backend feature, there is no direct impact on the end-user UI or CLI in this phase.
- Future CLI/UI features will be built on top of this persistence layer.
- **Error Handling:** The ingestion script and repository methods should raise clear, specific exceptions for scenarios like:
  - Database connection failure.
  - Missing metadata or HTML files during ingestion.
  - Permissions errors when moving media files.

## 7. Validation

1.  **Install Dependencies:**
    - Run `poetry install` to ensure `sqlalchemy` and `alembic` are installed.
2.  **Static Analysis and Typing:**
    - `poetry run ruff check .`
    - `poetry run mypy .`
3.  **Database Migration:**
    - Run `poetry run alembic revision --autogenerate -m "Create initial models"` to create the first migration.
    - Run `poetry run alembic upgrade head` to apply it.
4.  **Run Tests:**
    - `poetry run pytest tests/test_persistence.py`
5.  **Manual Verification:**
    - Run the ingestion script: `poetry run python -m src.doughub.ingestion`.
    - Inspect the created `doughub.db` file with a SQLite browser to confirm that data has been ingested correctly.
    - Verify that image files have been copied to the `media_root/` directory.
    - Add `doughub.db` and `media_root/` to `.gitignore`.
