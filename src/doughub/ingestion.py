"""Ingestion script for importing question extractions into the database.

This module scans the extractions/ directory and imports all found questions
and their associated media files into the SQLite database.
"""

import json
import logging
import shutil
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import doughub.config as config
from doughub.models import Base
from doughub.persistence import QuestionRepository

logger = logging.getLogger(__name__)


def parse_extraction_filename(filename: str) -> tuple[str, str] | None:
    """Parse extraction filename to extract source name and question key.

    Expected format: YYYYMMDD_HHMMSS_SourceName_QuestionKey.ext
    Example: 20251116_150929_MKSAP_19_0.json

    Args:
        filename: Name of the extraction file.

    Returns:
        Tuple of (source_name, question_key) or None if parsing fails.
    """
    parts = filename.split("_")
    if len(parts) < 4:
        return None

    # Extract timestamp (first 2 parts), then source name and question key
    # YYYYMMDD_HHMMSS_Source_Key or YYYYMMDD_HHMMSS_Source_Name_Key
    timestamp_parts = 2
    remaining = parts[timestamp_parts:]

    # The last part before extension is the key
    # Everything in between is the source name
    if len(remaining) < 2:
        return None

    question_key = remaining[-1].split(".")[0]  # Remove extension
    source_name = "_".join(remaining[:-1])

    return source_name, question_key


def find_media_files(base_path: Path, base_filename: str) -> list[Path]:
    """Find all media files associated with a question.

    Media files follow the pattern: {base_filename}_img{N}.{ext}

    Args:
        base_path: Directory containing the extraction files.
        base_filename: Base filename without extension (e.g., "20251116_150929_MKSAP_19_0").

    Returns:
        List of paths to associated media files.
    """
    media_files = []
    for ext in ["jpg", "jpeg", "png", "gif", "webp"]:
        # Find all files matching the pattern
        pattern = f"{base_filename}_img*"
        for media_file in base_path.glob(f"{pattern}.{ext}"):
            media_files.append(media_file)

    return sorted(media_files)


def get_mime_type(file_path: Path) -> str:
    """Determine MIME type from file extension.

    Args:
        file_path: Path to the file.

    Returns:
        MIME type string.
    """
    ext = file_path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "application/octet-stream")


def copy_media_to_storage(
    media_file: Path, source_name: str, question_key: str, media_index: int
) -> str:
    """Copy media file to the media storage directory.

    Args:
        media_file: Path to the source media file.
        source_name: Name of the source.
        question_key: Unique key of the question.
        media_index: Index of this media file.

    Returns:
        Relative path to the copied media file.
    """
    # Create source-specific directory
    media_root = Path(config.MEDIA_ROOT)
    source_dir = media_root / source_name
    source_dir.mkdir(parents=True, exist_ok=True)

    # Create destination filename
    ext = media_file.suffix
    dest_filename = f"{question_key}_img{media_index}{ext}"
    dest_path = source_dir / dest_filename

    # Copy file
    shutil.copy2(media_file, dest_path)
    logger.info(f"Copied media file: {media_file} -> {dest_path}")

    # Return relative path
    return f"{source_name}/{dest_filename}"


def ingest_question(
    repo: QuestionRepository,
    json_path: Path,
    html_path: Path,
    source_name: str,
    question_key: str,
) -> None:
    """Ingest a single question and its media into the database.

    Args:
        repo: QuestionRepository instance.
        json_path: Path to the JSON metadata file.
        html_path: Path to the HTML content file.
        source_name: Name of the source.
        question_key: Unique key of the question within the source.
    """
    # Read JSON metadata
    with open(json_path, encoding="utf-8") as f:
        metadata = json.load(f)

    # Read HTML content
    with open(html_path, encoding="utf-8") as f:
        html_content = f.read()

    # Get or create source
    source = repo.get_or_create_source(name=source_name)

    # Check if question already exists
    source_id: int = source.source_id  # type: ignore[assignment]
    existing_question = repo.get_question_by_source_key(source_id, question_key)
    if existing_question:
        logger.info(
            f"Question already exists: {source_name}/{question_key} (ID: {existing_question.question_id})"
        )
        return

    # Add question
    question_data = {
        "source_id": source_id,
        "source_question_key": question_key,
        "raw_html": html_content,
        "raw_metadata_json": json.dumps(metadata),
        "status": "extracted",
        "extraction_path": str(json_path.parent / json_path.stem),
    }

    question = repo.add_question(question_data)
    logger.info(f"Added question: {source_name}/{question_key} (ID: {question.question_id})")

    # Find and process media files
    base_filename = json_path.stem  # Remove .json extension
    media_files = find_media_files(json_path.parent, base_filename)

    for idx, media_file in enumerate(media_files):
        # Copy media to storage
        relative_path = copy_media_to_storage(
            media_file, source_name, question_key, idx
        )

        # Add media record
        media_data = {
            "media_role": "image",
            "media_type": "question_image",
            "mime_type": get_mime_type(media_file),
            "relative_path": relative_path,
        }
        question_id: int = question.question_id  # type: ignore[assignment]
        media = repo.add_media_to_question(question_id, media_data)
        logger.info(f"  Added media: {relative_path} (ID: {media.media_id})")


def ingest_extractions(
    extractions_dir: str = "extractions",
    database_url: str | None = None,
) -> None:
    """Scan the extractions directory and ingest all questions.

    Args:
        extractions_dir: Path to the extractions directory.
        database_url: Optional database URL. If None, uses config.DATABASE_URL.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    db_url = database_url or config.DATABASE_URL
    logger.info(f"Using database: {db_url}")

    # Create engine and session
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    extractions_path = Path(extractions_dir)
    if not extractions_path.exists():
        logger.error(f"Extractions directory not found: {extractions_dir}")
        return

    # Find all JSON files
    json_files = list(extractions_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files")

    # Create session and repository
    session = SessionLocal()
    repo = QuestionRepository(session)

    try:
        for json_file in json_files:
            # Parse filename
            parsed = parse_extraction_filename(json_file.name)
            if not parsed:
                logger.warning(f"Could not parse filename: {json_file.name}")
                continue

            source_name, question_key = parsed

            # Find corresponding HTML file
            html_file = json_file.with_suffix(".html")
            if not html_file.exists():
                logger.warning(f"HTML file not found for: {json_file.name}")
                continue

            try:
                ingest_question(repo, json_file, html_file, source_name, question_key)
                # Commit after each successful question to avoid rolling back previously ingested questions
                repo.commit()
            except Exception as e:
                logger.error(f"Error ingesting {json_file.name}: {e}", exc_info=True)
                session.rollback()

        logger.info("Ingestion completed successfully")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        repo.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    ingest_extractions()
