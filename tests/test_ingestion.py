import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.ingestion import (
    call_extraction_llm,
    copy_media_to_storage,
    find_media_files,
    get_mime_type,
    ingest_question,
    load_extraction_prompt,
    parse_extraction_filename,
)
from doughub.models import Base, Media, Question, Source
from doughub.persistence import QuestionRepository
from doughub.ui.dto import MinimalQuestion, MinimalQuestionBatch

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


class TestCleanSlateIngestion:
    """Tests for the new clean slate extraction mode using MinimalQuestionBatch."""
    
    @pytest.fixture
    def mock_files(self, tmp_path):
        """Create dummy extraction files."""
        json_path = tmp_path / "test.json"
        html_path = tmp_path / "test.html"
        
        with open(json_path, "w") as f:
            json.dump({"title": "Test Question"}, f)
            
        with open(html_path, "w") as f:
            f.write("<div>Raw HTML Content</div>")
            
        return json_path, html_path

    def test_ingest_with_minimal_data_populates_new_fields(self, repo, mock_files):
        """Test that providing MinimalQuestionBatch populates question_context_html and question_stem_html."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        # Create minimal data
        minimal_data = MinimalQuestionBatch(
            questions=[
                MinimalQuestion(
                    question_context_html="<p>Context for the question</p>",
                    question_stem_html="<p>What is the correct answer?</p>"
                )
            ]
        )
        
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=minimal_data)
        
        # Verify question was created with new fields populated
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        assert question is not None
        assert question.question_context_html == "<p>Context for the question</p>"
        assert question.question_stem_html == "<p>What is the correct answer?</p>"
        
        # Verify raw fields are still populated
        assert question.raw_html == "<div>Raw HTML Content</div>"
        assert "Test Question" in question.raw_metadata_json

    def test_ingest_with_minimal_data_leaves_old_fields_null(self, repo, mock_files):
        """Test that old parsed fields remain NULL when using clean slate mode."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        minimal_data = MinimalQuestionBatch(
            questions=[
                MinimalQuestion(
                    question_context_html="<p>Context</p>",
                    question_stem_html="<p>Question</p>"
                )
            ]
        )
        
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=minimal_data)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        # Verify old fields are not populated (remain NULL)
        assert question.is_parsed is None
        assert question.cleaned_question_html is None
        assert question.cleaned_explanation_html is None
        assert question.cleaned_answers_json is None

    def test_ingest_without_minimal_data_leaves_all_optional_fields_null(self, repo, mock_files):
        """Test that when minimal_data is not provided, all optional fields remain NULL."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        # Ingest without minimal_data (backward compatibility mode)
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=None)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        assert question is not None
        
        # Verify new minimal schema fields are NULL
        assert question.question_context_html is None
        assert question.question_stem_html is None
        
        # Verify old fields are also NULL
        assert question.is_parsed is None
        assert question.cleaned_question_html is None
        assert question.cleaned_explanation_html is None
        assert question.cleaned_answers_json is None
        
        # But raw fields should still be populated
        assert question.raw_html == "<div>Raw HTML Content</div>"
        assert "Test Question" in question.raw_metadata_json

    def test_ingest_with_empty_context(self, repo, mock_files):
        """Test that empty context (default value) is handled correctly."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        minimal_data = MinimalQuestionBatch(
            questions=[
                MinimalQuestion(
                    question_context_html="",  # Empty context
                    question_stem_html="<p>Question without context</p>"
                )
            ]
        )
        
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=minimal_data)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        assert question.question_context_html == ""
        assert question.question_stem_html == "<p>Question without context</p>"

    def test_ingest_minimal_data_with_multiple_questions_uses_first(self, repo, mock_files):
        """Test that when batch contains multiple questions, only the first is used."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        minimal_data = MinimalQuestionBatch(
            questions=[
                MinimalQuestion(
                    question_context_html="<p>First Context</p>",
                    question_stem_html="<p>First Question</p>"
                ),
                MinimalQuestion(
                    question_context_html="<p>Second Context</p>",
                    question_stem_html="<p>Second Question</p>"
                )
            ]
        )
        
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=minimal_data)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        # Should use the first question from the batch
        assert question.question_context_html == "<p>First Context</p>"
        assert question.question_stem_html == "<p>First Question</p>"

    def test_ingest_minimal_data_with_empty_batch_leaves_fields_null(self, repo, mock_files):
        """Test that an empty MinimalQuestionBatch leaves new fields NULL."""
        json_path, html_path = mock_files
        source_name = "Test_Source"
        question_key = "1"
        
        minimal_data = MinimalQuestionBatch(questions=[])
        
        ingest_question(repo, json_path, html_path, source_name, question_key, minimal_data=minimal_data)
        
        source = repo.get_source_by_name(source_name)
        question = repo.get_question_by_source_key(source.source_id, question_key)
        
        # Empty batch should not populate the fields
        assert question.question_context_html is None
        assert question.question_stem_html is None


class TestLLMExtraction:
    """Tests for LLM-based extraction functionality."""
    
    def test_load_extraction_prompt(self):
        """Test that the extraction prompt can be loaded successfully."""
        prompt = load_extraction_prompt()
        
        assert prompt is not None
        assert len(prompt) > 0
        assert "question_context_html" in prompt
        assert "question_stem_html" in prompt
        assert "Exclusion Rules" in prompt
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "")
    def test_call_extraction_llm_requires_endpoint(self):
        """Test that LLM extraction fails when endpoint is not configured."""
        with pytest.raises(ValueError, match="LLM_API_ENDPOINT is not configured"):
            call_extraction_llm("<p>Test HTML</p>")
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", False)
    def test_call_extraction_llm_requires_enabled(self):
        """Test that LLM extraction fails when not enabled."""
        with pytest.raises(ValueError, match="LLM extraction is not enabled"):
            call_extraction_llm("<p>Test HTML</p>")
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.config.LLM_API_KEY", "test-api-key")
    @patch("doughub.ingestion.config.LLM_MODEL", "gpt-4")
    @patch("doughub.ingestion.httpx.Client")
    def test_call_extraction_llm_success(self, mock_client_class):
        """Test successful LLM extraction with mocked HTTP response."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "questions": [
                                {
                                    "question_context_html": "<p>A 45-year-old woman presents with chest pain.</p>",
                                    "question_stem_html": "<p>What is the most appropriate next step?</p>"
                                }
                            ]
                        })
                    }
                }
            ]
        }
        
        # Configure mock client
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Call the function
        html_content = "<p>A 45-year-old woman presents with chest pain.</p><p>What is the most appropriate next step?</p>"
        result = call_extraction_llm(html_content)
        
        # Verify the result
        assert isinstance(result, MinimalQuestionBatch)
        assert len(result.questions) == 1
        assert result.questions[0].question_context_html == "<p>A 45-year-old woman presents with chest pain.</p>"
        assert result.questions[0].question_stem_html == "<p>What is the most appropriate next step?</p>"
        
        # Verify the API was called correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.example.com/v1/chat/completions"
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.config.LLM_API_KEY", "test-api-key")
    @patch("doughub.ingestion.httpx.Client")
    def test_call_extraction_llm_handles_markdown_wrapped_json(self, mock_client_class):
        """Test that LLM extraction handles JSON wrapped in markdown code blocks."""
        # Create a mock response with markdown-wrapped JSON
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "```json\n" + json.dumps({
                            "questions": [
                                {
                                    "question_context_html": "",
                                    "question_stem_html": "<p>Which of the following is correct?</p>"
                                }
                            ]
                        }) + "\n```"
                    }
                }
            ]
        }
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        result = call_extraction_llm("<p>Which of the following is correct?</p>")
        
        assert isinstance(result, MinimalQuestionBatch)
        assert len(result.questions) == 1
        assert result.questions[0].question_stem_html == "<p>Which of the following is correct?</p>"
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.httpx.Client")
    def test_call_extraction_llm_handles_http_error(self, mock_client_class):
        """Test that LLM extraction properly handles HTTP errors."""
        import httpx
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.HTTPError("Connection failed")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(httpx.HTTPError):
            call_extraction_llm("<p>Test HTML</p>")
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.httpx.Client")
    def test_call_extraction_llm_handles_invalid_json(self, mock_client_class):
        """Test that LLM extraction handles invalid JSON responses."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is not valid JSON"
                    }
                }
            ]
        }
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with pytest.raises(json.JSONDecodeError):
            call_extraction_llm("<p>Test HTML</p>")
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.httpx.Client")
    def test_call_extraction_llm_handles_validation_error(self, mock_client_class):
        """Test that LLM extraction handles schema validation errors."""
        # Missing required field question_stem_html
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "questions": [
                                {
                                    "question_context_html": "<p>Context</p>"
                                    # Missing question_stem_html
                                }
                            ]
                        })
                    }
                }
            ]
        }
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            call_extraction_llm("<p>Test HTML</p>")
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.httpx.Client")
    def test_ingest_question_with_llm_extraction(self, mock_client_class, repo, tmp_path):
        """Test full ingestion flow with LLM extraction enabled."""
        # Set up mock LLM response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "questions": [
                                {
                                    "question_context_html": "<p>Patient presents with symptoms.</p>",
                                    "question_stem_html": "<p>What is the diagnosis?</p>"
                                }
                            ]
                        })
                    }
                }
            ]
        }
        
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Create test files
        json_path = tmp_path / "test.json"
        html_path = tmp_path / "test.html"
        
        with open(json_path, "w") as f:
            json.dump({"title": "Test Question"}, f)
        with open(html_path, "w") as f:
            f.write("<p>Patient presents with symptoms.</p><p>What is the diagnosis?</p>")
        
        # Ingest the question
        ingest_question(repo, json_path, html_path, "Test_Source", "1")
        
        # Verify the question was created with LLM-extracted data
        source = repo.get_source_by_name("Test_Source")
        question = repo.get_question_by_source_key(source.source_id, "1")
        
        assert question is not None
        assert question.question_context_html == "<p>Patient presents with symptoms.</p>"
        assert question.question_stem_html == "<p>What is the diagnosis?</p>"
        
        # Verify LLM was called
        mock_client.post.assert_called_once()
    
    @patch("doughub.ingestion.config.ENABLE_LLM_EXTRACTION", True)
    @patch("doughub.ingestion.config.LLM_API_ENDPOINT", "https://api.example.com/v1/chat/completions")
    @patch("doughub.ingestion.httpx.Client")
    def test_ingest_question_llm_failure_continues_gracefully(self, mock_client_class, repo, tmp_path):
        """Test that ingestion continues even if LLM extraction fails."""
        import httpx
        
        # Set up mock to raise an error
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.HTTPError("API Error")
        mock_client_class.return_value = mock_client
        
        # Create test files
        json_path = tmp_path / "test.json"
        html_path = tmp_path / "test.html"
        
        with open(json_path, "w") as f:
            json.dump({"title": "Test Question"}, f)
        with open(html_path, "w") as f:
            f.write("<p>Test HTML content</p>")
        
        # Ingest the question - should not raise, just log error
        ingest_question(repo, json_path, html_path, "Test_Source", "1")
        
        # Verify the question was still created, but without extracted fields
        source = repo.get_source_by_name("Test_Source")
        question = repo.get_question_by_source_key(source.source_id, "1")
        
        assert question is not None
        assert question.raw_html == "<p>Test HTML content</p>"
        assert question.question_context_html is None
        assert question.question_stem_html is None

