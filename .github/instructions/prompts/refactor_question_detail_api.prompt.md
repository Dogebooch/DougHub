### 1. Overview

- **Summary:** Refactor `MainWindow` and `QuestionDetailView` so the question detail pane uses the new `populate_view(QuestionDetailDTO)` API instead of the deprecated `set_question(...)`. Introduce a clear `QuestionDetailDTO` factory layer and a temporary compatibility wrapper to avoid breaking behavior during the transition.
- **Goals:**
    - Eliminate the `set_question is deprecated` warnings from the logs.
    - Restore and stabilize rendering of question details in the “Extracted Questions” tab.
    - Make `QuestionDetailView` depend only on `QuestionDetailDTO`, not on any legacy DTO types.
- **Design Principle Note:** Implementation must follow DougHub’s layered UI design: list DTOs for lists, detail DTOs for detail views, and a single entry point for updating a view (`populate_view`) without incidental complexity.

### 2. Context & Constraints

- **Files:**
    - `src/doughub/ui/main_window.py` – owns the question list UI and reacts to selection changes.
    - `src/doughub/ui/question_detail_view.py` – renders the detail view for a single question.
    - `src/doughub/ui/dto.py` – defines `QuestionDTO` and `QuestionDetailDTO`.
- **Current State:**
    - `QuestionDetailView` exposes a new `populate_view(self, dto: QuestionDetailDTO)` API.
    - A deprecated `set_question(...)` method still exists and logs a warning on every call.
    - `MainWindow` still calls `set_question(...)` in `_on_question_selected(...)`.
    - The detail pane is not rendering question content, indicating a mismatch between DTO/results and view logic.
- **Constraints:**
    - No changes to how HTML/extracted question data is fetched from the network or persisted. Only the UI wiring between selection and detail view is in scope.
    - The final design must have one public, non-deprecated way to populate the detail view: `populate_view(QuestionDetailDTO)`.

### 3. Implementation Checkpoints

#### 3.1 Make `QuestionDetailDTO` the Canonical Detail DTO

- **File(s):** `src/doughub/ui/dto.py`
- **Actions:**
    1.  Inspect `QuestionDetailDTO` and ensure it explicitly represents everything the detail view needs, including:
        - Question identifier (`id`).
        - Any display metadata (source, topic, tags, flags).
        - Extracted question content for the “extracted questions” tab (e.g., `context_html`, `stem_html`).
    2.  Add classmethod factory helpers to avoid ad-hoc construction:
        - `@classmethod from_model(cls, question_model, *, extracted=None) -> QuestionDetailDTO`: Builds a detail DTO from the question domain model and any extracted data.
        - `@classmethod empty(cls) -> QuestionDetailDTO`: Returns a DTO representing the "no selection / clear state".
    3.  Ensure these factories are typed, documented, and have basic unit tests.

#### 3.2 Introduce a Compatibility Wrapper in `QuestionDetailView`

- **File(s):** `src/doughub/ui/question_detail_view.py`
- **Actions:**
    1.  Implement `populate_view(self, dto: QuestionDetailDTO) -> None` as the **only** method that mutates the UI and binds data to widgets.
    2.  Temporarily keep `set_question(...)` but make it a thin compatibility wrapper:
        - It should accept the legacy DTO type (likely `QuestionDTO | None`).
        - It logs the deprecation warning.
        - It internally converts the `QuestionDTO` into a `QuestionDetailDTO` by calling the new factory (`QuestionDetailDTO.from_model(...)`).
        - If the argument is `None`, it calls `populate_view(QuestionDetailDTO.empty())`.
    3.  Ensure that even when called, the deprecated path still renders the view correctly so the app remains functional during the refactor.

#### 3.3 Update `MainWindow` to Use `populate_view(QuestionDetailDTO)`

- **File(s):** `src/doughub/ui/main_window.py`
- **Actions:**
    1.  Add an explicit import for `QuestionDetailDTO`.
    2.  Refactor `_on_question_selected(...)` to fetch the domain model.
    3.  If `question_id` is `None` or the repository returns `None`, call `self.question_detail_view.populate_view(QuestionDetailDTO.empty())`.
    4.  If a question is found, build the detail DTO using the canonical factory (`detail_dto = QuestionDetailDTO.from_model(question)`) and call `self.question_detail_view.populate_view(detail_dto)`.
    5.  Wrap repository and DTO construction in a `try/except` block. On exception, log the error and call `populate_view(QuestionDetailDTO.empty())` to prevent leaving the view in a stale state.

#### 3.4 Remove All Remaining Uses of `set_question`

- **File(s):** All `src/doughub/ui/*.py` files
- **Actions:**
    1.  Search the entire repository for any remaining calls to `set_question(`.
    2.  For each call site found, replace it with a call to `populate_view(QuestionDetailDTO)` using the same factory pattern as in `_on_question_selected`.
    3.  After all callers are updated, run the application and confirm that no deprecation warnings appear in the logs during UI navigation.

#### 3.5 Remove the Deprecated `set_question` Method

- **File(s):** `src/doughub/ui/question_detail_view.py`
- **Actions:**
    1.  After verifying that no call sites remain and no warnings are logged, remove the `set_question` method entirely from `QuestionDetailView`.
    2.  Optionally, add a comment near `populate_view` documenting it as the canonical API.

### 4. Behavior Changes

- **End-user behavior:** The question detail pane will resume rendering correctly. This refactor fixes the blank-view bug caused by the deprecated method no longer populating the UI.
- **Developer-facing behavior:** `QuestionDetailView` will now have a single, stable entry point: `populate_view(QuestionDetailDTO)`. The legacy `set_question(...)` method is fully removed after a safe transition period.

### 5. Validation

- **Static checks:**
    - `ruff check .`
    - `mypy src/ tests/`
- **Unit/integration tests:**
    - Add tests for `QuestionDetailDTO.from_model(...)` and `.empty()` to ensure they produce valid DTOs.
    - Add tests for `QuestionDetailView.populate_view(...)` verifying widgets are updated correctly from a sample DTO.
    - Update tests for `_on_question_selected(...)` to confirm it calls `populate_view` with the correct DTO for valid, missing, and error states.
    - Verify no test calls `set_question(...)`.
- **Manual UI verification:**
    - Run `python src/doughub/main.py`.
    - Open the “Extracted Questions” tab.
    - Select several questions and confirm the detail view populates correctly.
    - Confirm **no `set_question is deprecated` warnings appear in the logs.**
    - Clear the selection or select an invalid item and confirm the view returns to a clean empty state.
