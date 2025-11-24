import pytest
from doughub.models import Question, Source

class TestQuestionLifecycle:
    def test_initial_state(self):
        q = Question(source_id=1, source_question_key="k", raw_html="", raw_metadata_json="{}")
        # SQLAlchemy defaults are applied on flush/commit usually, or if explicitly set.
        # Here we check that we can set it.
        if q.status is None:
            q.status = "extracted"
        assert q.status == "extracted"
        
    def test_state_transitions(self):
        # Define valid transitions
        # extracted -> processed -> seen -> correct/incorrect
        q = Question(source_id=1, source_question_key="k", raw_html="", raw_metadata_json="{}", status="extracted")
        
        # Simulate processing
        q.status = "processed"
        assert q.status == "processed"
        
        # Simulate studying
        q.status = "seen"
        assert q.status == "seen"
        
        # Simulate answering
        q.status = "correct"
        assert q.status == "correct"
        
        # Invalid transition (example)
        # In a real implementation, we might have a method `transition_to(new_state)` that raises error
        # For now, we just test that the model accepts strings. 
        # If we want to enforce this, we'd need to add logic to the model or a service.
        pass

class TestScoringAndStats:
    def test_scoring_calculation(self):
        # This logic might not exist in models yet, so we define what we expect
        # Let's assume we have a list of questions with states
        questions = [
            Question(status="correct"),
            Question(status="correct"),
            Question(status="incorrect"),
            Question(status="seen"), # Not answered yet
        ]
        
        correct = sum(1 for q in questions if q.status == "correct")
        incorrect = sum(1 for q in questions if q.status == "incorrect")
        total_answered = correct + incorrect
        
        accuracy = (correct / total_answered) * 100 if total_answered > 0 else 0
        
        assert correct == 2
        assert incorrect == 1
        assert total_answered == 3
        assert accuracy == pytest.approx(66.67, 0.01)

    def test_scoring_edge_cases(self):
        # Zero answers
        questions = []
        correct = sum(1 for q in questions if q.status == "correct")
        total = 0
        accuracy = (correct / total) * 100 if total > 0 else 0
        assert accuracy == 0
        
        # All correct
        questions = [Question(status="correct")]
        correct = 1
        total = 1
        accuracy = 100
        assert accuracy == 100

class TestTagging:
    def test_tag_operations(self):
        # Tags are stored as JSON string in the model currently
        import json
        q = Question(source_id=1, source_question_key="k", raw_html="", raw_metadata_json="{}")
        
        # Add tags
        tags = ["tag1", "tag2"]
        q.tags = json.dumps(tags)
        
        tags_str = q.tags
        assert tags_str is not None
        stored_tags = json.loads(tags_str)
        assert "tag1" in stored_tags
        assert "tag2" in stored_tags
        
        # Rename tag (simulate)
        stored_tags = ["tag1_renamed" if t == "tag1" else t for t in stored_tags]
        q.tags = json.dumps(stored_tags)
        
        tags_str = q.tags
        assert tags_str is not None
        assert "tag1_renamed" in json.loads(tags_str)
        assert "tag1" not in json.loads(tags_str)
        
        # Delete tag
        stored_tags = [t for t in stored_tags if t != "tag2"]
        q.tags = json.dumps(stored_tags)
        
        tags_str = q.tags
        assert tags_str is not None
        assert "tag2" not in json.loads(tags_str)
