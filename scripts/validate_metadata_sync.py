"""Manual validation script for Phase 3 metadata sync.

This script demonstrates the metadata sync feature by:
1. Creating a test question in the database
2. Creating a note file with metadata in the frontmatter
3. Running the sync process
4. Verifying the metadata was synced to the database
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub import config
from doughub.models import Base
from doughub.notebook.sync import scan_and_parse_notes
from doughub.persistence.repository import QuestionRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run manual validation of metadata sync."""
    logger.info("Starting Phase 3 metadata sync validation")

    # Initialize database
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = QuestionRepository(session)

    try:
        # Step 1: Create a test source and question
        logger.info("Step 1: Creating test question in database")
        source = repo.get_or_create_source("Test_Source", "Validation test")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "validation_q1",
            "raw_html": "<p>Test question for validation</p>",
            "raw_metadata_json": '{"title": "Validation Question"}',
            "status": "extracted",
        }
        question = repo.add_question(question_data)
        repo.commit()
        logger.info(f"Created question {question.question_id}")

        # Step 2: Create a note file for this question
        logger.info("Step 2: Creating note file with metadata")
        notes_dir = Path(config.NOTES_DIR)
        notes_dir.mkdir(parents=True, exist_ok=True)

        note_path = notes_dir / "Test_Source_validation_q1.md"
        note_content = f"""---
question_id: {question.question_id}
source: Test_Source
tags: ["validation", "test", "cardiology"]
state: review
---

# Notes

This is a test note created for validation purposes.
"""
        note_path.write_text(note_content, encoding="utf-8")
        logger.info(f"Created note file: {note_path}")

        # Update note_path in database
        question.note_path = str(note_path)
        repo.commit()

        # Step 3: Check initial state
        logger.info("Step 3: Checking initial question state")
        initial = repo.get_question_by_id(question.question_id)
        assert initial is not None
        logger.info(f"  Initial tags: {initial.tags}")
        logger.info(f"  Initial state: {initial.state}")

        # Step 4: Run sync
        logger.info("Step 4: Running metadata sync")
        sync_count = 0
        for metadata in scan_and_parse_notes(notes_dir):
            if repo.update_question_from_metadata(metadata):
                sync_count += 1
        repo.commit()
        logger.info(f"  Synced {sync_count} question(s)")

        # Step 5: Verify sync
        logger.info("Step 5: Verifying synced metadata")
        synced = repo.get_question_by_id(question.question_id)
        assert synced is not None
        logger.info(f"  Synced tags: {synced.tags}")
        logger.info(f"  Synced state: {synced.state}")

        # Validate results
        assert synced.tags == '["validation", "test", "cardiology"]'
        assert synced.state == "review"

        logger.info("✓ Validation PASSED - Metadata sync working correctly!")
        return 0

    except Exception as e:
        logger.error(f"✗ Validation FAILED: {e}", exc_info=True)
        repo.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
