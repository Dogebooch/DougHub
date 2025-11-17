"""Test script for notebook note creation functionality.

This script demonstrates the ensure_note_for_question functionality
by creating stub notes for questions in the database.
"""

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.config import DATABASE_URL, NOTES_DIR
from doughub.persistence import QuestionRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_note_creation() -> None:
    """Test creating notes for existing questions."""
    logger.info(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=False)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    repo = QuestionRepository(session)

    try:
        # Get a few questions to test with
        questions = repo.get_all_questions()[:5]  # Test with first 5 questions

        if not questions:
            logger.warning("No questions found in database. Run load_test_db.py first.")
            return

        logger.info(f"Found {len(questions)} questions to test with")
        logger.info(f"Notes directory: {NOTES_DIR}")

        for question in questions:
            logger.info(f"\nProcessing question {question.question_id}:")
            logger.info(f"  Source: {question.source.name}")
            logger.info(f"  Key: {question.source_question_key}")

            # Create note (idempotent - safe to call multiple times)
            note_path = repo.ensure_note_for_question(int(question.question_id))  # type: ignore[arg-type]

            if note_path:
                logger.info(f"  ✓ Note created/verified: {note_path}")

                # Verify file exists
                if Path(note_path).exists():
                    logger.info("  ✓ File exists on disk")

                    # Show first few lines
                    with open(note_path, encoding="utf-8") as f:
                        first_lines = "".join(f.readlines()[:10])
                        logger.info(f"  Content preview:\n{first_lines}")
                else:
                    logger.error(f"  ✗ File not found: {note_path}")
            else:
                logger.error("  ✗ Failed to create note")

        # Commit changes
        repo.commit()
        logger.info("\n✓ All notes created successfully")

        # Test idempotency - try creating again
        logger.info("\nTesting idempotency (calling ensure_note_for_question again)...")
        for question in questions:
            note_path = repo.ensure_note_for_question(int(question.question_id))  # type: ignore[arg-type]
            logger.info(f"  Question {question.question_id}: {note_path}")

        repo.commit()
        logger.info("✓ Idempotency test passed")

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        repo.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    test_note_creation()
