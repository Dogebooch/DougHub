import json

from doughub.models import Media, Question
from doughub.ui.dto import QuestionDTO


def test_question_dto_from_model_valid() -> None:
    metadata = {
        "answers": [
            {"text": "Answer 1", "is_correct": True, "peer_percentage": 80.5},
            {"text": "Answer 2", "is_correct": False, "peer_percentage": 19.5},
        ],
        "explanation": "<p>Explanation</p>"
    }
    question = Question(
        question_id=1,
        raw_html="<p>Question</p>",
        raw_metadata_json=json.dumps(metadata),
        media=[]
    )

    dto = QuestionDTO.from_model(question)

    assert dto.question_id == 1
    assert dto.question_text_html == "<p>Question</p>"
    assert dto.explanation_html == "<p>Explanation</p>"
    assert len(dto.answers) == 2
    assert dto.answers[0].text == "Answer 1"
    assert dto.answers[0].is_correct is True
    assert dto.answers[0].peer_percentage == 80.5
    assert dto.image_path is None


def test_question_dto_from_model_malformed_json() -> None:
    question = Question(
        question_id=1,
        raw_html="<p>Question</p>",
        raw_metadata_json="invalid json",
        media=[]
    )

    dto = QuestionDTO.from_model(question)

    assert dto.question_id == 1
    assert dto.answers == []
    assert dto.explanation_html == "<i>No explanation provided.</i>"


def test_question_dto_from_model_missing_keys() -> None:
    metadata: dict[str, list[dict[str, str]]] = {"answers": [{"text": "A1"}]} # Missing is_correct, peer_percentage
    question = Question(
        question_id=1,
        raw_html="<p>Question</p>",
        raw_metadata_json=json.dumps(metadata),
        media=[]
    )

    dto = QuestionDTO.from_model(question)

    assert len(dto.answers) == 1
    assert dto.answers[0].text == "A1"
    assert dto.answers[0].is_correct is False
    assert dto.answers[0].peer_percentage is None


def test_question_dto_from_model_with_image() -> None:
    metadata: dict[str, str] = {}
    media = Media(media_role="image", relative_path="path/to/image.jpg")
    question = Question(
        question_id=1,
        raw_html="<p>Question</p>",
        raw_metadata_json=json.dumps(metadata),
        media=[media]
    )

    # Mock config.MEDIA_ROOT
    import doughub.config as config
    original_media_root = config.MEDIA_ROOT
    config.MEDIA_ROOT = "/media"

    try:
        dto = QuestionDTO.from_model(question)
        assert dto.image_path is not None
        # On windows it might be backslash, so check endswith or normalize
        assert dto.image_path.replace("\\", "/").endswith("media/path/to/image.jpg")
    finally:
        config.MEDIA_ROOT = original_media_root
