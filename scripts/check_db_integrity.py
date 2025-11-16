"""Database integrity validation script.

This read-only script validates the integrity of the DougHub database,
checking for orphaned records, missing media files, and other data issues.
"""

import argparse
import logging
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from doughub.config import DATABASE_URL, MEDIA_ROOT
from doughub.models import Base, Media, Question, Source

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_orphaned_media(session) -> list[str]:
    """Check for media records with missing question references.

    Args:
        session: Database session.

    Returns:
        List of error messages for orphaned media.
    """
    errors = []
    stmt = select(Media)
    media_records = session.execute(stmt).scalars().all()

    for media in media_records:
        stmt = select(Question).where(Question.question_id == media.question_id)
        question = session.execute(stmt).scalar_one_or_none()
        if question is None:
            errors.append(
                f"Orphaned media: media_id={media.media_id}, "
                f"question_id={media.question_id}, path={media.relative_path}"
            )

    return errors


def check_missing_media_files(session) -> list[str]:
    """Check for media records pointing to non-existent files.

    Args:
        session: Database session.

    Returns:
        List of error messages for missing files.
    """
    errors = []
    media_root = Path(MEDIA_ROOT)
    stmt = select(Media)
    media_records = session.execute(stmt).scalars().all()

    for media in media_records:
        file_path = media_root / media.relative_path
        if not file_path.exists():
            errors.append(
                f"Missing file: media_id={media.media_id}, "
                f"path={media.relative_path}, full_path={file_path}"
            )

    return errors


def check_orphaned_questions(session) -> list[str]:
    """Check for questions with invalid source references.

    Args:
        session: Database session.

    Returns:
        List of error messages for orphaned questions.
    """
    errors = []
    stmt = select(Question)
    questions = session.execute(stmt).scalars().all()

    for question in questions:
        stmt = select(Source).where(Source.source_id == question.source_id)
        source = session.execute(stmt).scalar_one_or_none()
        if source is None:
            errors.append(
                f"Orphaned question: question_id={question.question_id}, "
                f"source_id={question.source_id}, key={question.source_question_key}"
            )

    return errors


def check_duplicate_questions(session) -> list[str]:
    """Check for duplicate (source_id, source_question_key) pairs.

    Args:
        session: Database session.

    Returns:
        List of warning messages for duplicates.
    """
    warnings = []
    stmt = select(Question)
    questions = session.execute(stmt).scalars().all()

    seen = set()
    for question in questions:
        key = (question.source_id, question.source_question_key)
        if key in seen:
            warnings.append(
                f"Duplicate question key: source_id={question.source_id}, "
                f"key={question.source_question_key}"
            )
        seen.add(key)

    return warnings


def check_empty_required_fields(session) -> list[str]:
    """Check for questions with empty required fields.

    Args:
        session: Database session.

    Returns:
        List of error messages for invalid data.
    """
    errors = []
    stmt = select(Question)
    questions = session.execute(stmt).scalars().all()

    for question in questions:
        if not question.raw_html or not question.raw_html.strip():
            errors.append(
                f"Empty raw_html: question_id={question.question_id}, "
                f"key={question.source_question_key}"
            )
        if not question.raw_metadata_json or not question.raw_metadata_json.strip():
            errors.append(
                f"Empty raw_metadata_json: question_id={question.question_id}, "
                f"key={question.source_question_key}"
            )

    return errors


def print_summary(
    sources_count: int,
    questions_count: int,
    media_count: int,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Print a summary report of the database check.

    Args:
        sources_count: Number of sources in the database.
        questions_count: Number of questions in the database.
        media_count: Number of media records in the database.
        errors: List of error messages.
        warnings: List of warning messages.
    """
    print("\n" + "=" * 60)
    print("DATABASE INTEGRITY CHECK REPORT")
    print("=" * 60)
    print("\nDatabase Statistics:")
    print(f"  Sources:   {sources_count}")
    print(f"  Questions: {questions_count}")
    print(f"  Media:     {media_count}")

    if not errors and not warnings:
        print("\n✓ No issues found. Database integrity is good.")
    else:
        if errors:
            print(f"\n✗ Found {len(errors)} error(s):")
            for error in errors:
                print(f"  - {error}")

        if warnings:
            print(f"\n⚠ Found {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")

    print("=" * 60 + "\n")


def main() -> None:
    """Run database integrity checks and print a summary report."""
    parser = argparse.ArgumentParser(
        description="Validate DougHub database integrity (read-only)"
    )
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help=f"Database URL (default: {DATABASE_URL})",
    )
    parser.add_argument(
        "--media-root",
        default=MEDIA_ROOT,
        help=f"Media root directory (default: {MEDIA_ROOT})",
    )

    args = parser.parse_args()

    logger.info(f"Checking database: {args.database_url}")
    logger.info(f"Media root: {args.media_root}")

    # Override config if provided
    if args.media_root != MEDIA_ROOT:
        import doughub.config as config
        config.MEDIA_ROOT = args.media_root

    # Connect to database (read-only)
    engine = create_engine(args.database_url, echo=False)

    # Verify schema exists
    Base.metadata.reflect(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Gather statistics
        sources_count = session.execute(select(Source)).scalars().all()
        questions_count = session.execute(select(Question)).scalars().all()
        media_count = session.execute(select(Media)).scalars().all()

        # Run checks
        all_errors = []
        all_warnings = []

        logger.info("Checking for orphaned media...")
        all_errors.extend(check_orphaned_media(session))

        logger.info("Checking for missing media files...")
        all_errors.extend(check_missing_media_files(session))

        logger.info("Checking for orphaned questions...")
        all_errors.extend(check_orphaned_questions(session))

        logger.info("Checking for duplicate questions...")
        all_warnings.extend(check_duplicate_questions(session))

        logger.info("Checking for empty required fields...")
        all_errors.extend(check_empty_required_fields(session))

        # Print summary
        print_summary(
            len(sources_count),
            len(questions_count),
            len(media_count),
            all_errors,
            all_warnings,
        )

    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()
