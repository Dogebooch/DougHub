### 1. Overview

*   **Summary:** Establish a clear baseline for the existing test suite by discovering how tests are run and measuring code coverage.
*   **Goals:**
    *   Find the canonical test commands from project configuration.
    *   Run tests to ensure they pass.
    *   Generate a code coverage report.
    *   Identify well-covered, partially-covered, and uncovered modules.
*   **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard.

### 2. Context & Constraints

*   **Repo Mapping:** `pyproject.toml`, `tests/`, `src/doughub/`
*   **Technology:** Python, `pytest`, `pytest-cov`.
*   **Constraints:**
    *   Use existing tools and configurations discovered in the previous step.
    *   Do not add or modify tests in this step.
    *   The goal is to measure the current state, not change it.

### 3. Implementation Checkpoints

1.  **Discover Test Command:**
    *   **File(s):** `pyproject.toml`, `README.md`
    *   **Action:** Examine `pyproject.toml` and `README.md` to find the standard command for running tests. Assume `pytest` is the runner and look for configuration under the `[tool.pytest.ini_options]` section.
    *   **Risks / Edge Cases:** The command might be in a CI file or a script. If not found, check `.github/` workflows.
2.  **Run Tests:**
    *   **File(s):** N/A (command execution)
    *   **Action:** Execute the discovered test command (e.g., `pytest`) and confirm that the test suite passes without errors.
    *   **Risks / Edge Cases:** Tests may fail, which should be noted in the summary.
3.  **Generate Coverage Report:**
    *   **File(s):** N/A (command execution)
    *   **Action:** Run `pytest` with coverage enabled (e.g., `pytest --cov=src/doughub --cov-report=term-missing`) to generate a report.
    *   **Risks / Edge Cases:** The `pytest-cov` plugin might not be installed. Note this if the command fails.
4.  **Summarize Test State:**
    *   **File(s):** N/A (output is text)
    *   **Action:** Produce a summary of the current testing state, including the pass/fail status and a list of modules that are well-covered, partially-covered, and uncovered, based on the coverage report.
    *   **Risks / Edge Cases:** The coverage report can be misleading. The summary should be presented as a quantitative baseline.

### 4. Behavior Changes

*   None. This is a read-only analysis task.

### 5. End-User Experience (UX)

*   Not applicable.

### 6. Validation

*   **Commands / Checks:**
    *   `pytest`
    *   `pytest --cov=src/doughub --cov-report=term-missing`
*   **Expected Results:**
    *   `pytest` exits with code 0.
    *   A coverage report is printed to the terminal.
    *   A summary report is produced.
*   **Manual QA Checklist:**
    *   Does the summary accurately reflect the test run outcome?
    *   Does the summary list specific uncovered or poorly-tested files?
    *   Is the command used to generate coverage included in the summary?
