# Plan: Consolidated Automatic Question Grouping and Display

## 1. Overview

This is a consolidated plan to implement a robust question grouping feature. It combines previous plans for manual and automatic grouping into a single, comprehensive strategy and adds a new display format for the question browser.

The core of this plan is to **automatically group** related extractions (e.g., a question and its explanation) using a heuristic based on their source URL and extraction time. To handle potential errors in automation, a **manual override** UI will be provided.

Finally, the question browser's display will be updated to show the question ID and its associated topic in the format: `Q <ID> (<Topic>) - [X parts]`.

**Goals:**
*   Automatically group related extractions upon creation.
*   Update the question browser to display both the question identifier and its topic.
*   Provide a simple UI for users to view and correct these automatic groupings.
*   Create a single, coherent implementation plan for the entire feature.

**Non-Goals:**
*   This plan will not rely on parsing filenames or HTML content for grouping.
*   The core Tampermonkey extraction script will not be changed.

## 2. Context and Constraints

*   **Automation Logic:** The core grouping logic will reside in `scripts/extraction_server.py`.
*   **Database:** The plan requires a database migration to add a `parent_id` for self-referential relationships on the `questions` table.
*   **Key Files:**
    *   `src/doughub/models.py`: For the schema change.
    *   `scripts/extraction_server.py`: To house the automatic grouping logic.
    *   `src/doughub/ui/question_browser_view.py`: To update the display format and provide the override UI.
    *   `src/doughub/ui/main_window.py`: To handle the override logic.
    *   `src/doughub/ui/dto.py`: To pass grouped data to the UI.
    *   A new UI file for the "Manage Group" dialog.

## 3. Implementation Checkpoints

### Checkpoint 1: Update Database Schema

**File to Edit:** `src/doughub/models.py`
**Task:** Introduce a self-referential relationship on the `Question` model to allow questions to be linked together in a parent-child structure.

1.  **Modify Model:** In the `Question` class, add the `parent_id` column and the `children` relationship.

    ```python
    # In src/doughub/models.py, update the Question class
    class Question(Base):
        # ... existing columns ...
        updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
        parent_id = Column(Integer, ForeignKey("questions.id"), nullable=True) # <-- ADD THIS

        # Relationships
        source = relationship("Source", back_populates="questions")
        media = relationship("Media", back_populates="question", cascade="all, delete-orphan")
        children = relationship("Question", backref=backref('parent', remote_side=[question_id]), cascade="all, delete-orphan") # <-- AND ADD THIS

        def __repr__(self) -> str:
            # ...
    ```

2.  **Generate Migration:** Create the Alembic migration script.
    ```sh
    alembic revision --autogenerate -m "Add parent_id to questions for grouping"
    ```
3.  **Apply Migration:** Run the migration to update the database.
    ```sh
    alembic upgrade head
    ```

### Checkpoint 2: Implement Automatic Grouping Logic

**File to Edit:** `scripts/extraction_server.py`
**Task:** After persisting a new question, attempt to automatically link it to a suitable parent question based on a heuristic.

1.  **Modify `persist_to_database`:** After the `question` is created and before the final commit, add a call to a new helper function that performs the grouping.

    ```python
    # In scripts/extraction_server.py, inside persist_to_database
    # ... after question = repo.add_question(question_data) ...
    
    # Attempt to group this new question automatically
    _group_question_automatically(question, repo.session)

    # ... before repo.commit() ...
    ```

2.  **Implement `_group_question_automatically`:** This function contains the core heuristic.

    ```python
    # In scripts/extraction_server.py
    from datetime import timedelta
    from sqlalchemy import and_

    def _group_question_automatically(new_question: Question, session):
        """Try to link a new question to a recent, ungrouped parent from the same source."""
        # Heuristic: Link if from the same source and within 5 minutes
        time_window = timedelta(minutes=5)
        
        potential_parent = session.query(Question).filter(
            and_(
                Question.source_id == new_question.source_id,
                Question.parent_id.is_(None),
                Question.question_id != new_question.question_id,
                Question.created_at >= (new_question.created_at - time_window),
                Question.created_at < new_question.created_at
            )
        ).order_by(Question.created_at.desc()).first()

        if potential_parent:
            new_question.parent_id = potential_parent.question_id
            print(f"[DB] Automatically grouped question {new_question.question_id} under parent {potential_parent.question_id}")

    ```

### Checkpoint 3: Update UI for Grouped Display

**Files to Edit:**
*   `src/doughub/ui/question_browser_view.py`
*   `src/doughub/ui/dto.py`
*   `src/doughub/ui/question_detail_view.py`

**Task:** Refactor the UI to handle the new parent-child data structure and the desired display format.

1.  **Browser View (`question_browser_view.py`):**
    *   In `load_questions`, modify the query to only fetch questions where `parent_id` is `NULL`. Eagerly load the `source` and `children` relationships to prevent N+1 query issues.
    *   When populating the `QListWidget`, set the item's text using the new format.

    ```python
    # In question_browser_view.py's method for populating the list
    for question in top_level_questions:
        # The 'source' and 'children' should be eagerly loaded in the query
        topic = question.source.name if question.source else "Unknown"
        num_parts = len(question.children) + 1
        display_text = f"Q {question.question_id} ({topic}) - [{num_parts} parts]"
        # Create and add QListWidgetItem with display_text
    ```

2.  **DTO (`dto.py`):** Ensure the `QuestionDTO` can hold child DTOs and that the `from_model` classmethod populates them recursively.

3.  **Detail View (`question_detail_view.py`):** Update `set_question` to render the parent question's content first, followed by the content of all its children to create a single, consolidated view.

### Checkpoint 4: Implement Manual Override UI

**Task:** Create a dialog that allows a user to manually unlink items from an automatically created group.

1.  **Context Menu (`question_browser_view.py`):**
    *   Add a context menu action named "Manage Group..." to items in the list.
    *   This action should only be enabled if the selected question has children.
    *   It should emit a signal with the `question_id` of the selected parent question.
2.  **Create Dialog (`src/doughub/ui/manage_group_dialog.py`):**
    *   Create a new `QDialog` that takes a parent `question_id`.
    *   The dialog will list the child questions, each with an "Unlink" button.
3.  **Add Logic (`main_window.py`):**
    *   Create a slot in `MainWindow` to open the `ManageGroupDialog`.
    *   Handle the signal from the "Unlink" button to set the child's `parent_id` to `NULL` in the database, and then trigger a UI refresh.

## 4. Behavior Changes

*   **Automatic Linking:** Extractions from the same source URL within a few minutes of each other will now be automatically linked.
*   **New Display Format:** The question browser will display items as `Q <ID> (<Topic>) - [X parts]`.
*   **Manual Override:** The primary manual action is now *unlinking* via the "Manage Group" dialog.

## 5. End-User Experience

1.  A user extracts a question, then its explanation from the same webpage.
2.  The system automatically links them. The question browser refreshes, showing a single entry like: `Q 123 (MKSAP 19) - [2 parts]`.
3.  If the grouping is incorrect, the user can right-click the item, select "Manage Group...", and click "Unlink" on the incorrect part. The UI will then update to show the two items separately.

## 6. Validation

1.  **Migration:** Confirm `alembic upgrade head` completes successfully.
2.  **Automatic Grouping Test:**
    *   Extract item A from a source. Within 1 minute, extract item B from the same source.
    *   **Verify:** The question browser shows a single item with the format `Q <ID> (<Topic>) - [2 parts]`.
    *   **Verify:** The detail view shows the content of both A and B.
3.  **No Grouping Test (Time):**
    *   Extract item A. Wait > 5 minutes. Extract item C from the same source.
    *   **Verify:** The browser shows two separate items.
4.  **Manual Override Test:**
    *   Perform the successful automatic grouping test.
    *   Right-click the grouped item and use "Manage Group..." to unlink an item.
    *   **Verify:** The browser view updates to show the two items separately, each with the format `... [1 part]`.
5.  **Code Quality:** Run `pytest`, `ruff check .`, and `mypy .` to ensure no regressions and high code quality.
