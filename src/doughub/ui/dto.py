import json
import logging
import os
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

import doughub.config as config
from doughub.models import Question

logger = logging.getLogger(__name__)

@dataclass
class AnswerDTO:
    """DTO for a single answer choice."""
    text: str
    is_correct: bool
    peer_percentage: float | None = None

@dataclass
class QuestionDTO:
    """DTO for displaying a question, parsed robustly from the database model."""
    question_id: int
    question_text_html: str
    answers: list[AnswerDTO]
    explanation_html: str
    image_path: str | None = None
    children: list['QuestionDTO'] = field(default_factory=list)

    @classmethod
    def from_model(cls, question_model: Question) -> 'QuestionDTO':
        """Parses a Question model instance into a UI-friendly DTO."""
        try:
            metadata = json.loads(question_model.raw_metadata_json)
        except (json.JSONDecodeError, TypeError):
            metadata = {}
            logger.warning(f"Could not parse metadata JSON for Question ID: {question_model.question_id}")

        parsed_answers = []
        for ans_data in metadata.get('answers', []):
            if not isinstance(ans_data, dict):
                continue
            parsed_answers.append(AnswerDTO(
                text=ans_data.get('text', '<i>No answer text provided.</i>'),
                is_correct=ans_data.get('is_correct', False),
                peer_percentage=ans_data.get('peer_percentage')
            ))

        # Resolve image path against MEDIA_ROOT
        image_path = None
        if question_model.media:
            image_media = next((m for m in question_model.media if m.media_role == 'image'), None)
            if image_media:
                image_path = os.path.join(config.MEDIA_ROOT, image_media.relative_path)

        dto = cls(
            question_id=question_model.question_id,
            question_text_html=question_model.raw_html or "<i>No question content.</i>",
            answers=parsed_answers,
            explanation_html=metadata.get('explanation', '<i>No explanation provided.</i>'),
            image_path=image_path
        )

        # Recursively populate children
        if question_model.children:
            dto.children = [cls.from_model(child) for child in question_model.children]

        return dto


class MinimalQuestion(BaseModel):
    """Minimal schema for new extraction pipeline.
    
    Represents a question with just context and stem HTML.
    Context is optional, stem is required.
    """
    question_context_html: str = Field(default="", description="Optional context HTML for the question")
    question_stem_html: str = Field(description="Required HTML content of the question stem")


class MinimalQuestionBatch(BaseModel):
    """Batch of minimal questions for processing."""
    questions: list[MinimalQuestion] = Field(description="List of minimal questions to process")
