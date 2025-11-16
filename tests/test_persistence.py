"""Tests for the persistence layer (models, repository, and ingestion)."""

import json
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from doughub.models import Base, Media, Question, Source
from doughub.persistence import QuestionRepository


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repo(session):
    """Create a QuestionRepository for testing."""
    return QuestionRepository(session)


class TestQuestionRepository:
    """Tests for the QuestionRepository class."""

    def test_get_or_create_source_creates_new(self, repo: QuestionRepository) -> None:
        """Test that get_or_create_source creates a new source."""
        source = repo.get_or_create_source("MKSAP", "Medical Knowledge Self-Assessment Program")
        repo.commit()

        assert source.source_id is not None
        assert source.name == "MKSAP"
        assert source.description == "Medical Knowledge Self-Assessment Program"

    def test_get_or_create_source_is_idempotent(self, repo: QuestionRepository) -> None:
        """Test that get_or_create_source returns existing source."""
        source1 = repo.get_or_create_source("MKSAP", "Description 1")
        repo.commit()

        source2 = repo.get_or_create_source("MKSAP", "Description 2")
        repo.commit()

        assert source1.source_id == source2.source_id
        # Description should remain unchanged from first creation
        assert source2.description == "Description 1"

    def test_add_question_creates_new(self, repo: QuestionRepository) -> None:
        """Test that add_question creates a new question."""
        source = repo.get_or_create_source("MKSAP")
        repo.commit()

        question_data = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Question content</html>",
            "raw_metadata_json": json.dumps({"url": "https://example.com"}),
            "status": "extracted",
        }

        question = repo.add_question(question_data)
        repo.commit()

        assert question.question_id is not None
        assert question.source_id == source.source_id
        assert question.source_question_key == "q001"
        assert question.raw_html == "<html>Question content</html>"

    def test_add_question_is_idempotent(self, repo: QuestionRepository) -> None:
        """Test that adding the same question twice updates instead of creating duplicate."""
        source = repo.get_or_create_source("MKSAP")
        repo.commit()

        question_data1 = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Original content</html>",
            "raw_metadata_json": json.dumps({"version": 1}),
            "status": "extracted",
        }

        question1 = repo.add_question(question_data1)
        repo.commit()
        question1_id = question1.question_id

        # Add the same question again with different content
        question_data2 = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Updated content</html>",
            "raw_metadata_json": json.dumps({"version": 2}),
            "status": "processed",
        }

        question2 = repo.add_question(question_data2)
        repo.commit()

        # Should be the same question ID
        assert question2.question_id == question1_id
        # Content should be updated
        assert question2.raw_html == "<html>Updated content</html>"
        assert question2.status == "processed"

        # Verify only one question exists
        all_questions = repo.get_all_questions()
        assert len(all_questions) == 1

    def test_add_question_missing_required_field(self, repo: QuestionRepository) -> None:
        """Test that add_question raises ValueError for missing required fields."""
        question_data = {
            "source_id": 1,
            "source_question_key": "q001",
            # Missing raw_html and raw_metadata_json
        }

        with pytest.raises(ValueError, match="Missing required field"):
            repo.add_question(question_data)

    def test_add_media_to_question(self, repo: QuestionRepository) -> None:
        """Test adding media to a question."""
        source = repo.get_or_create_source("MKSAP")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Content</html>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        media_data = {
            "media_role": "image",
            "media_type": "question_image",
            "mime_type": "image/jpeg",
            "relative_path": "MKSAP/q001_img0.jpg",
        }

        media = repo.add_media_to_question(question.question_id, media_data)
        repo.commit()

        assert media.media_id is not None
        assert media.question_id == question.question_id
        assert media.media_role == "image"
        assert media.relative_path == "MKSAP/q001_img0.jpg"

    def test_add_media_missing_required_field(self, repo: QuestionRepository) -> None:
        """Test that add_media_to_question raises ValueError for missing required fields."""
        media_data = {
            "media_role": "image",
            # Missing mime_type and relative_path
        }

        with pytest.raises(ValueError, match="Missing required field"):
            repo.add_media_to_question(1, media_data)

    def test_get_question_by_id(self, repo: QuestionRepository) -> None:
        """Test retrieving a question by ID."""
        source = repo.get_or_create_source("MKSAP")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Content</html>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        retrieved = repo.get_question_by_id(question.question_id)
        assert retrieved is not None
        assert retrieved.question_id == question.question_id

        # Non-existent ID
        assert repo.get_question_by_id(999999) is None

    def test_get_question_by_source_key(self, repo: QuestionRepository) -> None:
        """Test retrieving a question by source and key."""
        source = repo.get_or_create_source("MKSAP")
        question_data = {
            "source_id": source.source_id,
            "source_question_key": "q001",
            "raw_html": "<html>Content</html>",
            "raw_metadata_json": "{}",
        }
        question = repo.add_question(question_data)
        repo.commit()

        retrieved = repo.get_question_by_source_key(source.source_id, "q001")
        assert retrieved is not None
        assert retrieved.question_id == question.question_id

        # Non-existent key
        assert repo.get_question_by_source_key(source.source_id, "q999") is None

    def test_get_all_questions(self, repo: QuestionRepository) -> None:
        """Test retrieving all questions."""
        source1 = repo.get_or_create_source("MKSAP")
        source2 = repo.get_or_create_source("Peerprep")

        for i in range(3):
            repo.add_question({
                "source_id": source1.source_id,
                "source_question_key": f"q{i:03d}",
                "raw_html": f"<html>Q{i}</html>",
                "raw_metadata_json": "{}",
            })

        for i in range(2):
            repo.add_question({
                "source_id": source2.source_id,
                "source_question_key": f"q{i:03d}",
                "raw_html": f"<html>Q{i}</html>",
                "raw_metadata_json": "{}",
            })

        repo.commit()

        # Get all questions
        all_questions = repo.get_all_questions()
        assert len(all_questions) == 5

        # Filter by source
        mksap_questions = repo.get_all_questions(source_id=source1.source_id)
        assert len(mksap_questions) == 3

        peerprep_questions = repo.get_all_questions(source_id=source2.source_id)
        assert len(peerprep_questions) == 2

    def test_get_source_by_name(self, repo: QuestionRepository) -> None:
        """Test retrieving a source by name."""
        source = repo.get_or_create_source("MKSAP")
        repo.commit()

        retrieved = repo.get_source_by_name("MKSAP")
        assert retrieved is not None
        assert retrieved.source_id == source.source_id

        # Non-existent name
        assert repo.get_source_by_name("NonExistent") is None


class TestIngestion:
    """Tests for the ingestion module."""

    def test_parse_extraction_filename(self) -> None:
        """Test parsing extraction filenames."""
        from doughub.ingestion import parse_extraction_filename

        # Valid filenames
        result = parse_extraction_filename("20251116_150929_MKSAP_19_0.json")
        assert result == ("MKSAP_19", "0")

        result = parse_extraction_filename("20251116_145626_ACEP_PeerPrep_2.html")
        assert result == ("ACEP_PeerPrep", "2")

        # Invalid filenames
        assert parse_extraction_filename("invalid.json") is None
        assert parse_extraction_filename("20251116_MKSAP.json") is None

    def test_find_media_files(self) -> None:
        """Test finding media files for a question."""
        from doughub.ingestion import find_media_files

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            base = "20251116_150929_MKSAP_19_0"
            (tmppath / f"{base}.json").touch()
            (tmppath / f"{base}.html").touch()
            (tmppath / f"{base}_img0.jpg").touch()
            (tmppath / f"{base}_img1.png").touch()
            (tmppath / f"{base}_img2.gif").touch()

            media_files = find_media_files(tmppath, base)
            assert len(media_files) == 3
            assert all(f.exists() for f in media_files)

    def test_get_mime_type(self) -> None:
        """Test MIME type detection."""
        from doughub.ingestion import get_mime_type

        assert get_mime_type(Path("image.jpg")) == "image/jpeg"
        assert get_mime_type(Path("image.jpeg")) == "image/jpeg"
        assert get_mime_type(Path("image.png")) == "image/png"
        assert get_mime_type(Path("image.gif")) == "image/gif"
        assert get_mime_type(Path("image.webp")) == "image/webp"
        assert get_mime_type(Path("unknown.xyz")) == "application/octet-stream"


class TestIngestionIntegration:
    """Integration tests for the ingestion workflow."""

    def test_ingest_happy_path(
        self, synthetic_extraction_dir: Path, tmp_path: Path
    ) -> None:
        """Test successful ingestion of valid extractions."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from doughub.ingestion import ingest_extractions

        # Setup temporary media root
        media_root = tmp_path / "media"
        media_root.mkdir()

        # Run ingestion
        import doughub.config as config
        original_media_root = config.MEDIA_ROOT
        config.MEDIA_ROOT = str(media_root)

        try:
            # Create a temporary database file
            db_file = tmp_path / "test.db"
            db_url = f"sqlite:///{db_file}"

            ingest_extractions(
                extractions_dir=str(synthetic_extraction_dir),
                database_url=db_url,
            )

            # Verify database contents
            engine = create_engine(db_url)
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            repo = QuestionRepository(session)

            # Should have created 2 sources (PeerPrep and MKSAP_19)
            peerprep = repo.get_source_by_name("PeerPrep")
            mksap = repo.get_source_by_name("MKSAP_19")
            assert peerprep is not None
            assert mksap is not None

            # Should have created 3 valid questions (Q1, Q2, Q3)
            all_questions = repo.get_all_questions()
            assert len(all_questions) == 3

            # Verify Q1 has 2 media files
            peerprep_id: int = peerprep.source_id  # type: ignore
            q1 = repo.get_question_by_source_key(peerprep_id, "Q1")
            assert q1 is not None
            assert len(q1.media) == 2

            # Verify Q2 has 1 media file
            mksap_id: int = mksap.source_id  # type: ignore
            q2 = repo.get_question_by_source_key(mksap_id, "Q2")
            assert q2 is not None
            assert len(q2.media) == 1

            # Verify Q3 has no media
            q3 = repo.get_question_by_source_key(mksap_id, "Q3")
            assert q3 is not None
            assert len(q3.media) == 0

            # Verify media files were copied to storage
            assert (media_root / "PeerPrep" / "Q1_img0.jpg").exists()
            assert (media_root / "PeerPrep" / "Q1_img1.png").exists()
            assert (media_root / "MKSAP_19" / "Q2_img0.jpg").exists()

            session.close()

        finally:
            config.MEDIA_ROOT = original_media_root

    def test_ingest_idempotency(
        self, synthetic_extraction_dir: Path, tmp_path: Path
    ) -> None:
        """Test that running ingestion twice does not create duplicates."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from doughub.ingestion import ingest_extractions

        # Setup temporary media root
        media_root = tmp_path / "media"
        media_root.mkdir()

        import doughub.config as config
        original_media_root = config.MEDIA_ROOT
        config.MEDIA_ROOT = str(media_root)

        try:
            db_file = tmp_path / "test.db"
            db_url = f"sqlite:///{db_file}"

            # Run ingestion twice
            ingest_extractions(
                extractions_dir=str(synthetic_extraction_dir),
                database_url=db_url,
            )
            ingest_extractions(
                extractions_dir=str(synthetic_extraction_dir),
                database_url=db_url,
            )

            # Verify no duplicates
            engine = create_engine(db_url)
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            repo = QuestionRepository(session)

            all_questions = repo.get_all_questions()
            assert len(all_questions) == 3  # Should still be 3, not 6

            session.close()

        finally:
            config.MEDIA_ROOT = original_media_root

    def test_ingest_handles_errors_gracefully(
        self, synthetic_extraction_dir: Path, tmp_path: Path
    ) -> None:
        """Test that ingestion handles malformed files without crashing."""
        from doughub.ingestion import ingest_extractions

        # Setup temporary media root
        media_root = tmp_path / "media"
        media_root.mkdir()

        import doughub.config as config
        original_media_root = config.MEDIA_ROOT
        config.MEDIA_ROOT = str(media_root)

        try:
            db_file = tmp_path / "test.db"
            db_url = f"sqlite:///{db_file}"

            # Run ingestion - should not crash despite malformed JSON and missing HTML
            ingest_extractions(
                extractions_dir=str(synthetic_extraction_dir),
                database_url=db_url,
            )

            # Verify that valid questions were still imported
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            engine = create_engine(db_url)
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            repo = QuestionRepository(session)

            all_questions = repo.get_all_questions()
            assert len(all_questions) == 3  # Only the 3 valid ones

            session.close()

        finally:
            config.MEDIA_ROOT = original_media_root


class TestModels:
    """Tests for the SQLAlchemy models."""

    def test_source_creation(self, session: Session) -> None:
        """Test creating a Source."""
        source = Source(name="MKSAP", description="Test description")
        session.add(source)
        session.commit()

        assert source.source_id is not None
        assert source.name == "MKSAP"

    def test_question_creation(self, session: Session) -> None:
        """Test creating a Question."""
        source = Source(name="MKSAP")
        session.add(source)
        session.commit()

        question = Question(
            source_id=source.source_id,
            source_question_key="q001",
            raw_html="<html>Content</html>",
            raw_metadata_json="{}",
        )
        session.add(question)
        session.commit()

        assert question.question_id is not None
        assert question.source_id == source.source_id

    def test_media_creation(self, session: Session) -> None:
        """Test creating Media."""
        source = Source(name="MKSAP")
        session.add(source)
        session.flush()

        question = Question(
            source_id=source.source_id,
            source_question_key="q001",
            raw_html="<html>Content</html>",
            raw_metadata_json="{}",
        )
        session.add(question)
        session.flush()

        media = Media(
            question_id=question.question_id,
            media_role="image",
            mime_type="image/jpeg",
            relative_path="MKSAP/q001_img0.jpg",
        )
        session.add(media)
        session.commit()

        assert media.media_id is not None
        assert media.question_id == question.question_id

    def test_question_unique_constraint(self, session: Session) -> None:
        """Test that the unique constraint on (source_id, source_question_key) works."""
        from sqlalchemy.exc import IntegrityError

        source = Source(name="MKSAP")
        session.add(source)
        session.commit()

        question1 = Question(
            source_id=source.source_id,
            source_question_key="q001",
            raw_html="<html>Content 1</html>",
            raw_metadata_json="{}",
        )
        session.add(question1)
        session.commit()

        # Try to add a duplicate
        question2 = Question(
            source_id=source.source_id,
            source_question_key="q001",
            raw_html="<html>Content 2</html>",
            raw_metadata_json="{}",
        )
        session.add(question2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_relationships(self, session: Session) -> None:
        """Test that relationships work correctly."""
        source = Source(name="MKSAP")
        session.add(source)
        session.flush()

        question = Question(
            source_id=source.source_id,
            source_question_key="q001",
            raw_html="<html>Content</html>",
            raw_metadata_json="{}",
        )
        session.add(question)
        session.flush()

        media1 = Media(
            question_id=question.question_id,
            media_role="image",
            mime_type="image/jpeg",
            relative_path="MKSAP/q001_img0.jpg",
        )
        media2 = Media(
            question_id=question.question_id,
            media_role="image",
            mime_type="image/png",
            relative_path="MKSAP/q001_img1.png",
        )
        session.add_all([media1, media2])
        session.commit()

        # Test relationships
        assert len(source.questions) == 1
        assert source.questions[0].source_question_key == "q001"

        assert len(question.media) == 2
        assert question.source.name == "MKSAP"

