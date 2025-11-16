# Persistence Validation Quick Reference

## Test Commands

```powershell
# Run all persistence tests
pytest tests/test_persistence.py -v

# Run all logging tests
pytest tests/test_logging.py -v

# Run all tests together
pytest tests/test_persistence.py tests/test_logging.py -v

# Run specific test class
pytest tests/test_persistence.py::TestIngestionIntegration -v

# Run static analysis
ruff check src/doughub/persistence src/doughub/ingestion.py src/doughub/models.py src/doughub/cli.py tests/test_persistence.py tests/test_logging.py scripts/
```

## Database Tools

```powershell
# Check database integrity (default database)
python scripts/check_db_integrity.py

# Check custom database
python scripts/check_db_integrity.py --database-url sqlite:///path/to/db.db

# Generate load test data
python scripts/load_test_db.py

# Custom load test (50,000 questions)
python scripts/load_test_db.py --num-questions 50000 --num-sources 10
```

## CLI Commands

```powershell
# View all sources and question counts
doughub db source-summary

# View detailed question information
doughub db show-question <question_id>

# Examples
doughub db show-question 1
$env:DATABASE_URL='sqlite:///test.db'; doughub db source-summary
```

## Ingestion

```powershell
# Ingest from default extractions/ directory
python -m doughub.ingestion

# Ingest with custom paths
python -c "from doughub.ingestion import ingest_extractions; ingest_extractions('path/to/extractions', 'sqlite:///custom.db')"
```

## Test Fixtures

### test_db_session
- In-memory SQLite database
- Clean schema for each test
- Automatic cleanup

```python
def test_my_feature(test_db_session):
    repo = QuestionRepository(test_db_session)
    # ... test code
```

### synthetic_extraction_dir
- Temporary directory with test files
- Includes valid and invalid extractions
- Automatic cleanup

```python
def test_ingestion(synthetic_extraction_dir):
    # synthetic_extraction_dir contains:
    # - 20251116_145626_PeerPrep_Q1.json/.html + 2 images
    # - 20251116_150929_MKSAP_19_Q2.json/.html + 1 image
    # - 20251116_151354_MKSAP_19_Q3.json/.html (no images)
    # - 20251116_152000_PeerPrep_Q4.json (missing HTML)
    # - 20251116_152100_MKSAP_19_Q5.json/.html (malformed JSON)
```

## Database Models

### Source
- `source_id` (PK)
- `name` (unique)
- `description`

### Question
- `question_id` (PK)
- `source_id` (FK)
- `source_question_key` (unique with source_id)
- `raw_html`
- `raw_metadata_json`
- `status`
- `extraction_path`
- `created_at`
- `updated_at`

### Media
- `media_id` (PK)
- `question_id` (FK)
- `media_role`
- `media_type`
- `mime_type`
- `relative_path`

### Log
- `log_id` (PK)
- `level`
- `logger_name`
- `message`
- `timestamp`

## Common Patterns

### Create Test Database
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from doughub.models import Base
from doughub.persistence import QuestionRepository

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
repo = QuestionRepository(session)
```

### Add Question with Media
```python
# Create source
source = repo.get_or_create_source("MKSAP", "Medical Knowledge Assessment")

# Add question
question_data = {
    "source_id": source.source_id,
    "source_question_key": "q001",
    "raw_html": "<html>...</html>",
    "raw_metadata_json": '{"url": "..."}',
    "status": "extracted",
}
question = repo.add_question(question_data)

# Add media
media_data = {
    "media_role": "image",
    "mime_type": "image/jpeg",
    "relative_path": "MKSAP/q001_img0.jpg",
}
media = repo.add_media_to_question(question.question_id, media_data)

repo.commit()
```

### Use Persistent Logging
```python
import logging
from doughub.persistence.logging_handler import DatabaseLogHandler

logger = logging.getLogger("my_app")
handler = DatabaseLogHandler(session, level=logging.INFO)
logger.addHandler(handler)

logger.info("This will be saved to the database")
```

## Troubleshooting

### Tests Fail with Import Errors
```powershell
# Ensure package is installed in development mode
pip install -e .
```

### Database Already Exists Error
```powershell
# Stamp database with current revision
alembic stamp head

# Then create new migration
alembic revision --autogenerate -m "description"
```

### MEDIA_ROOT Not Updating in Tests
- Use `import doughub.config as config` and access as `config.MEDIA_ROOT`
- Do NOT use `from doughub.config import MEDIA_ROOT` (creates local copy)

## File Structure

```
src/doughub/
├── models.py                           # SQLAlchemy models (Source, Question, Media, Log)
├── ingestion.py                        # Extraction ingestion logic
├── cli.py                             # CLI with db inspection commands
└── persistence/
    ├── __init__.py
    ├── repository.py                  # QuestionRepository
    └── logging_handler.py             # DatabaseLogHandler

tests/
├── conftest.py                        # Shared fixtures
├── test_persistence.py                # Repository and ingestion tests
└── test_logging.py                    # Persistent logging tests

scripts/
├── check_db_integrity.py              # Database validation tool
└── load_test_db.py                    # Load testing tool

alembic/
└── versions/
    ├── eb6403123dde_create_initial_models.py
    └── 29896b7ef8fd_add_log_table_for_persistent_logging.py
```
