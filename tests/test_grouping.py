
import sys
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Add scripts directory to path to import extraction_server
sys.path.append(str(Path(__file__).parents[1] / "scripts"))

from extraction_server import _group_question_automatically  # type: ignore

from doughub.models import Base, Question, Source


@pytest.fixture
def engine() -> Engine:
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestAutomaticGrouping:
    """Tests for the automatic question grouping logic."""

    def create_question(
        self, session: Session, source: Source, key: str, created_at: datetime
    ) -> Question:
        """Helper to create a question with a specific timestamp."""
        question = Question(
            source_id=source.source_id,
            source_question_key=key,
            raw_html="<html></html>",
            raw_metadata_json="{}",
            created_at=created_at,
        )
        session.add(question)
        session.commit()
        return question

    def test_groups_within_time_window(self, session: Session) -> None:
        """Test that questions from same source within 5 mins are grouped."""
        source = Source(name="MKSAP")
        session.add(source)
        session.commit()

        base_time = datetime.now()

        # Create parent question
        q1 = self.create_question(session, source, "q1", base_time)

        # Create child question 2 minutes later
        q2 = self.create_question(session, source, "q2", base_time + timedelta(minutes=2))

        # Run grouping logic
        _group_question_automatically(q2, session)
        session.commit()

        assert q2.parent_id == q1.question_id

    def test_does_not_group_outside_time_window(self, session: Session) -> None:
        """Test that questions > 5 mins apart are NOT grouped."""
        source = Source(name="MKSAP")
        session.add(source)
        session.commit()

        base_time = datetime.now()

        # Create parent question
        self.create_question(session, source, "q1", base_time)

        # Create second question 6 minutes later
        q2 = self.create_question(session, source, "q2", base_time + timedelta(minutes=6))

        # Run grouping logic
        _group_question_automatically(q2, session)
        session.commit()

        assert q2.parent_id is None

    def test_does_not_group_different_sources(self, session: Session) -> None:
        """Test that questions from different sources are NOT grouped."""
        source1 = Source(name="MKSAP")
        source2 = Source(name="PeerPrep")
        session.add_all([source1, source2])
        session.commit()

        base_time = datetime.now()

        # Create parent question from source 1
        self.create_question(session, source1, "q1", base_time)

        # Create second question from source 2, 1 minute later
        q2 = self.create_question(session, source2, "q2", base_time + timedelta(minutes=1))

        # Run grouping logic
        _group_question_automatically(q2, session)
        session.commit()

        assert q2.parent_id is None

    def test_groups_multiple_children_to_same_parent(self, session: Session) -> None:
        """Test that multiple subsequent questions group to the same parent."""
        source = Source(name="MKSAP")
        session.add(source)
        session.commit()

        base_time = datetime.now()

        # Q1: Root
        q1 = self.create_question(session, source, "q1", base_time)

        # Q2: Child of Q1 (2 mins later)
        q2 = self.create_question(session, source, "q2", base_time + timedelta(minutes=2))
        _group_question_automatically(q2, session)
        session.commit()
        assert q2.parent_id == q1.question_id

        # Q3: Child of Q1 (3 mins later than Q1)
        # Note: Logic looks for parent created within 5 mins of Q3.
        # Q1 is 3 mins old. Q2 is 1 min old.
        # Q2 has parent_id set, so it's ignored as a potential parent.
        # Q1 has parent_id None, so it's a candidate.
        q3 = self.create_question(session, source, "q3", base_time + timedelta(minutes=3))
        _group_question_automatically(q3, session)
        session.commit()

        assert q3.parent_id == q1.question_id
