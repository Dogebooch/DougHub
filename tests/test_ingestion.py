import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.ingestion import (
    copy_media_to_storage,
    find_media_files,
    get_mime_type,
    ingest_question,
    parse_extraction_filename,
)
from doughub.models import Base, Media, Question, Source
from doughub.persistence import QuestionRepository

# Setup in-memory database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repo(db_session):
    return QuestionRepository(db_session)

class TestIngestionUtils:
    def test_parse_extraction_filename_valid(self):
        filename = "20251116_150929_MKSAP_19_0.json"
        result = parse_extraction_filename(filename)
        assert result == ("MKSAP_19", "0")

    def test_parse_extraction_filename_invalid(self):
        assert parse_extraction_filename("invalid_filename.json") is None
        assert parse_extraction_filename("20251116_150929.json") is None

    def test_get_mime_type(self):
        assert get_mime_type(Path("test.jpg")) == "image/jpeg"
        assert get_mime_type(Path("test.png")) == "image/png"
        assert get_mime_type(Path("test.unknown")) == "application/octet-stream"

    @patch("pathlib.Path.glob")
    def test_find_media_files(self, mock_glob):
        base_path = Path("/tmp")
        base_filename = "test_file"
        
        # Mock return values for glob
        mock_glob.side_effect = [
            [Path("/tmp/test_file_img0.jpg")], # jpg
            [], # jpeg
            [Path("/tmp/test_file_img1.png")], # png
            [], # gif
            []  # webp
        ]
        
        files = find_media_files(base_path, base_filename)
        assert len(files) == 2
        assert Path("/tmp/test_file_img0.jpg") in files
        assert Path("/tmp/test_file_img1.png") in files

class TestIngestionLogic:
    @pytest.fixture
    def mock_files(self, tmp_path):
        # Create dummy files
        json_path = tmp_path / "test.json"
        html_path = tmp_path / "test.html"
        
        with open(json_path, "w") as f:
            json.dump({"title": "Test Question"}, f)
            
        with open(html_path, "w") as f:
            f.write("<div>Test Content</div>")
            
        return json_path, html_path

    def test_ingest_question_basic(self, repo, mock_files):
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        ingest_question(repo, json_path, html_path, source_name, question_key)
        
        # Verify question was added
        question = repo.get_question_by_source_key(repo.get_source_by_name(source_name).source_id, question_key)
        assert question is not None
        assert question.raw_html == "<div>Test Content</div>"
        assert "Test Question" in question.raw_metadata_json

    def test_ingest_question_idempotency(self, repo, mock_files):
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        # First ingestion
        ingest_question(repo, json_path, html_path, source_name, question_key)
        question1 = repo.get_question_by_source_key(repo.get_source_by_name(source_name).source_id, question_key)
        
        # Second ingestion
        ingest_question(repo, json_path, html_path, source_name, question_key)
        question2 = repo.get_question_by_source_key(repo.get_source_by_name(source_name).source_id, question_key)
        
        assert question1.question_id == question2.question_id
        assert len(repo.get_all_questions()) == 1

    @patch("doughub.ingestion.copy_media_to_storage")
    @patch("doughub.ingestion.find_media_files")
    def test_ingest_question_with_media(self, mock_find, mock_copy, repo, mock_files):
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        # Mock media files
        mock_find.return_value = [Path("img1.jpg"), Path("img2.png")]
        mock_copy.side_effect = ["path/img1.jpg", "path/img2.png"]
        
        ingest_question(repo, json_path, html_path, source_name, question_key)
        
        question = repo.get_question_by_source_key(repo.get_source_by_name(source_name).source_id, question_key)
        assert len(question.media) == 2
        assert question.media[0].relative_path == "path/img1.jpg"

    @pytest.mark.parametrize("html_content", [
        "<div>Simple</div>",
        "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>", # Nested list
        "<table><tr><td>Cell</td></tr></table>", # Table
        "<div>" + "A" * 10000 + "</div>", # Long content
        "<div>Broken HTML", # Malformed
    ])
    def test_ingest_html_variability(self, repo, tmp_path, html_content):
        json_path = tmp_path / "test.json"
        html_path = tmp_path / "test.html"
        
        with open(json_path, "w") as f:
            json.dump({}, f)
        with open(html_path, "w") as f:
            f.write(html_content)
            
        ingest_question(repo, json_path, html_path, "Test_Source", "1")
        
        question = repo.get_question_by_source_key(repo.get_source_by_name("Test_Source").source_id, "1")
        assert question.raw_html == html_content

    def test_traceability_no_orphans(self, repo, mock_files):
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        ingest_question(repo, json_path, html_path, source_name, question_key)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        # Delete question
        repo.session.delete(question)
        repo.session.commit()
        
        # Verify no orphans (media should be deleted by cascade if configured, but let's check logic)
        # In this simple test, we just check that the question is gone.
        # Real orphan checks would involve checking the media table directly.
        assert repo.get_question_by_id(question.question_id) is None
        
        # Check media table
        media_count = repo.session.query(Media).filter(Media.question_id == question.question_id).count()
        assert media_count == 0

