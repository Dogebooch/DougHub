"""Repository for managing question persistence operations."""

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from doughub import config
from doughub.models import Media, Question, Source

logger = logging.getLogger(__name__)


def _serialize_tags(tags: Any) -> str | None:
    """Convert tags to a string representation for storage.

    Args:
        tags: Tags value from frontmatter (can be list, str, or None).

    Returns:
        JSON string representation of tags, or None.
    """
    if tags is None:
        return None
    if isinstance(tags, list):
        return json.dumps(tags)
    if isinstance(tags, str):
        # If already a string, store as-is (could be comma-separated or JSON)
        return tags
    # For other types, convert to JSON
    return json.dumps(tags)


class QuestionRepository:
    """Handles database operations for questions, sources, and media.

    This repository provides methods for creating, retrieving, and updating
    questions and their associated metadata in the database.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session

    def get_or_create_source(self, name: str, description: str | None = None) -> Source:
        """Find a source by name or create it if it doesn't exist.

        This method is idempotent - calling it multiple times with the same
        name will return the same source without creating duplicates.

        Args:
            name: Unique name of the source.
            description: Optional description of the source.

        Returns:
            The existing or newly created Source instance.
        """
        stmt = select(Source).where(Source.name == name)
        source = self.session.execute(stmt).scalar_one_or_none()

        if source is None:
            source = Source(name=name, description=description)
            self.session.add(source)
            self.session.flush()  # Get the source_id without committing

        return source

    def add_question(self, question_data: dict[str, Any]) -> Question:
        """Add a new question or update if it already exists.

        Uses the combination of source_id and source_question_key for
        idempotency. If a question with the same keys exists, it updates
        the existing record instead of creating a duplicate.

        Args:
            question_data: Dictionary containing:
                - source_id: ID of the source
                - source_question_key: Unique key within the source
                - raw_html: HTML content of the question
                - raw_metadata_json: JSON metadata as string
                - status: (optional) Status of the question
                - extraction_path: (optional) Original file path

        Returns:
            The created or updated Question instance.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["source_id", "source_question_key", "raw_html", "raw_metadata_json"]
        for field in required_fields:
            if field not in question_data:
                raise ValueError(f"Missing required field: {field}")

        # Check if question already exists
        stmt = select(Question).where(
            Question.source_id == question_data["source_id"],
            Question.source_question_key == question_data["source_question_key"]
        )
        question = self.session.execute(stmt).scalar_one_or_none()

        if question is None:
            # Create new question
            question = Question(**question_data)
            self.session.add(question)
            self.session.flush()
        else:
            # Update existing question
            for key, value in question_data.items():
                if key not in ["source_id", "source_question_key"]:  # Don't update keys
                    setattr(question, key, value)
            self.session.flush()

        return question

    def add_media_to_question(
        self, question_id: int, media_data: dict[str, Any]
    ) -> Media:
        """Add a media file associated with a question.

        Args:
            question_id: ID of the question this media belongs to.
            media_data: Dictionary containing:
                - media_role: Role of the media (e.g., 'image')
                - media_type: (optional) Type/subtype
                - mime_type: MIME type of the media
                - relative_path: Path relative to MEDIA_ROOT

        Returns:
            The created Media instance.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["media_role", "mime_type", "relative_path"]
        for field in required_fields:
            if field not in media_data:
                raise ValueError(f"Missing required field: {field}")

        media = Media(question_id=question_id, **media_data)
        self.session.add(media)
        self.session.flush()

        return media

    def get_question_by_id(self, question_id: int) -> Question | None:
        """Retrieve a question by its ID.

        Args:
            question_id: Primary key of the question.

        Returns:
            The Question instance or None if not found.
        """
        stmt = select(Question).where(Question.question_id == question_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_question_by_source_key(
        self, source_id: int, source_question_key: str
    ) -> Question | None:
        """Retrieve a question by its source and key.

        Args:
            source_id: ID of the source.
            source_question_key: Unique key within the source.

        Returns:
            The Question instance or None if not found.
        """
        stmt = select(Question).where(
            Question.source_id == source_id,
            Question.source_question_key == source_question_key
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_all_questions(self, source_id: int | None = None) -> list[Question]:
        """Retrieve all questions, optionally filtered by source.

        Args:
            source_id: Optional source ID to filter by.

        Returns:
            List of Question instances.
        """
        stmt = select(Question)
        if source_id is not None:
            stmt = stmt.where(Question.source_id == source_id)

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_source_by_name(self, name: str) -> Source | None:
        """Retrieve a source by its name.

        Args:
            name: Name of the source.

        Returns:
            The Source instance or None if not found.
        """
        stmt = select(Source).where(Source.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def update_question_from_metadata(self, metadata: dict[str, Any]) -> bool:
        """Update a question's metadata fields from parsed frontmatter.

        Extracts the question_id from metadata and updates the corresponding
        Question record with tags and state fields if present.

        Args:
            metadata: Dictionary containing at least 'question_id' and
                     optionally 'tags' and 'state' fields.

        Returns:
            True if the question was found and updated, False otherwise.
        """
        question_id = metadata.get("question_id")
        if question_id is None:
            logger.warning("Cannot update question: missing question_id in metadata")
            return False

        question = self.get_question_by_id(question_id)
        if question is None:
            logger.warning(f"Question {question_id} not found for metadata update")
            return False

        # Update tags if present
        if "tags" in metadata:
            question.tags = _serialize_tags(metadata["tags"])

        # Update state if present
        if "state" in metadata:
            state_value = metadata["state"]
            question.state = str(state_value) if state_value is not None else None

        self.session.flush()
        logger.debug(f"Updated metadata for question {question_id}")
        return True

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()

    def ensure_note_for_question(self, question_id: int) -> str | None:
        """Ensure a note file exists for the given question.

        Creates a stub markdown file with YAML frontmatter if it doesn't exist.
        Updates the question's note_path field in the database.
        This method is idempotent - multiple calls will not create duplicates.

        Args:
            question_id: ID of the question to create a note for.

        Returns:
            Path to the note file, or None if the question doesn't exist.

        Raises:
            OSError: If note file creation fails.
        """
        # Fetch the question
        question = self.get_question_by_id(question_id)
        if question is None:
            logger.warning(f"Question {question_id} not found")
            return None

        # If note already exists, return its path
        if question.note_path and Path(question.note_path).exists():
            logger.debug(f"Note already exists for question {question_id}: {question.note_path}")
            return question.note_path

        # Create notes directory if it doesn't exist
        notes_dir = Path(config.NOTES_DIR)
        notes_dir.mkdir(parents=True, exist_ok=True)

        # Generate note filename from source and question key
        # Sanitize filename by replacing problematic characters
        source_name = question.source.name.replace(" ", "_").replace("/", "_")
        safe_key = str(question.source_question_key).replace("/", "_").replace("\\", "_")
        note_filename = f"{source_name}_{safe_key}.md"
        note_path = notes_dir / note_filename

        # Create stub note with YAML frontmatter
        try:
            # Parse metadata if available
            metadata_dict = {}
            if question.raw_metadata_json:
                try:
                    metadata_dict = json.loads(str(question.raw_metadata_json))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse metadata JSON for question {question_id}")

            # Build YAML frontmatter
            frontmatter_lines = [
                "---",
                f"question_id: {question.question_id}",
                f"source: {question.source.name}",
                f"source_key: {question.source_question_key}",
                f"status: {question.status}",
            ]

            # Add selected metadata fields if available
            if "title" in metadata_dict:
                frontmatter_lines.append(f"title: {metadata_dict['title']}")
            if "category" in metadata_dict:
                frontmatter_lines.append(f"category: {metadata_dict['category']}")

            frontmatter_lines.append("---")
            frontmatter_lines.append("")  # Blank line after frontmatter

            # Write the stub note
            with open(note_path, "w", encoding="utf-8") as f:
                f.write("\n".join(frontmatter_lines))
                f.write("\n\n# Notes\n\n")
                f.write("<!-- Add your notes here -->\n")

            # Update the question's note_path
            question.note_path = str(note_path.absolute())
            self.session.flush()

            logger.info(f"Created note for question {question_id}: {note_path}")
            return str(note_path.absolute())

        except OSError as e:
            logger.error(f"Failed to create note file for question {question_id}: {e}")
            raise
