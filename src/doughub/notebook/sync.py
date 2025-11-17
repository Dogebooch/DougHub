"""Metadata sync service for syncing note frontmatter to database."""

import logging
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


def scan_and_parse_notes(notes_dir: Path) -> Iterator[dict[str, Any]]:
    """Scan notes directory and parse YAML frontmatter from markdown files.

    Walks the notes directory recursively, finds all .md files, and extracts
    YAML frontmatter. Errors in individual files are logged but do not stop
    the iteration.

    Args:
        notes_dir: Path to the directory containing note files.

    Yields:
        Dictionary containing parsed frontmatter with at least:
            - question_id: ID from the frontmatter
            - Other metadata fields as found in the frontmatter

    Example frontmatter:
        ---
        question_id: 42
        source: MKSAP_19
        tags: ["cardiology", "urgent"]
        state: review
        ---
    """
    if not notes_dir.exists():
        logger.warning(f"Notes directory does not exist: {notes_dir}")
        return

    if not notes_dir.is_dir():
        logger.error(f"Notes path is not a directory: {notes_dir}")
        return

    # Walk directory and find all .md files
    for md_file in notes_dir.rglob("*.md"):
        try:
            logger.debug(f"Processing note file: {md_file}")
            metadata = _parse_note_frontmatter(md_file)

            if metadata is None:
                logger.debug(f"No frontmatter found in {md_file}")
                continue

            # Ensure question_id is present
            if "question_id" not in metadata:
                logger.warning(f"Missing question_id in frontmatter: {md_file}")
                continue

            # Include file path for debugging
            metadata["_file_path"] = str(md_file)

            yield metadata

        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}", exc_info=True)
            continue


def _parse_note_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Dictionary of parsed frontmatter, or None if no frontmatter found.

    Raises:
        OSError: If file cannot be read.
        yaml.YAMLError: If frontmatter is invalid YAML.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Match YAML frontmatter block (--- at start, --- at end)
    # Pattern: start of file, ---, content, ---
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None

    frontmatter_text = match.group(1)

    try:
        # Parse YAML safely
        metadata = yaml.safe_load(frontmatter_text)

        if metadata is None:
            return {}

        if not isinstance(metadata, dict):
            logger.warning(f"Frontmatter is not a dict in {file_path}: {type(metadata)}")
            return None

        return metadata

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {file_path}: {e}")
        raise
