### 1. Overview

- **Summary:** This plan outlines a structural refactoring of the DougHub repository. The goal is to improve developer experience by organizing files more logically, consolidating scripts, and clarifying the project's dependency structure, without altering any application features.
- **Goals:**
  - Create a more intuitive and navigable directory structure.
  - Formalize the execution of utility and maintenance scripts.
  - Clean the root directory of transient files.
  - Structure the documentation to be more accessible.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard.

### 2. Context & Constraints

- **Repo Mapping:**
  - **Primary folders for refactoring:** `docs/`, `scripts/`.
  - **Root directory files:** `test_cli.db`, `package.json`.
  - **Configuration:** `pyproject.toml`, `.gitignore`.
- **Technology:** This is a PySide6 + QFluentWidgets desktop app. The presence of `package.json` suggests a hybrid project, which this plan will investigate.
- **Constraints:**
  - All existing application functionality must be retained.
  - The refactoring must not introduce breaking changes for the end-user.
  - All development and CI/CD workflows must continue to function after the changes.

### 3. Implementation Checkpoints

1. **Clean Root Directory and Update `.gitignore`**
   - **File(s):** `test_cli.db`, `.gitignore`
   - **Action:**
     - Move the `test_cli.db` file into a temporary directory or delete it.
     - Add `test_cli.db` and `*.db` to the `.gitignore` file to prevent similar files from being committed in the future.
   - **Risks / Edge Cases:** Ensure no test or application logic depends on this file being in the root directory.

2. **Organize `docs/` Directory**
   - **File(s):** All files within the `docs/` directory.
   - **Action:**
     - Create the following subdirectories within `docs/`: `architecture`, `process`, `validation`, and `ui`.
     - Move existing `.md` files into the appropriate new subdirectories based on their content. For example, `REFACTORING_UTILS.md` goes into `architecture`, `MANUAL_QA_CHECKLIST.md` goes into `validation`, and `UI_IMPLEMENTATION.md` goes into `ui`.
   - **Risks / Edge Cases:** Any hyperlinks within the documentation might need to be updated.

3. **Consolidate and Formalize Scripts**
   - **File(s):** `scripts/`, `pyproject.toml`
   - **Action:**
     - Analyze the Python scripts in the `scripts/` directory.
     - For scripts that are part of a regular workflow (e.g., `run_preflight_checks.py`, `check_db_integrity.py`), integrate them into `pyproject.toml` under the `[project.scripts]` table. This makes them executable as console commands (e.g., `doughub-preflight-checks`).
     - Move the remaining utility scripts into a more structured location, such as `tools/` or `src/doughub/cli/commands/`.
   - **Risks / Edge Cases:** Any existing shell scripts (`.ps1`) or developer workflows that call these Python scripts directly will need to be updated.

4. **Investigate and Clarify Node.js Usage**
   - **File(s):** `package.json`, `package-lock.json`, `node_modules/`
   - **Action:**
     - Investigate why `package.json` exists. Determine if it's for development tooling (e.g., linters, formatters) or if it is a remnant of a previous iteration.
     - If the Node.js dependencies are unused, remove `package.json`, `package-lock.json`, and add `node_modules/` to `.gitignore`.
     - If they are used for tooling, document their purpose and usage in `README.md`.
   - **Risks / Edge cases:** Removing these files could break a hidden dependency in the development or build process.

5. **Update `README.md`**
   - **File(s):** `README.md`
   - **Action:** Update the `README.md` to reflect the new directory structure and any changes to how scripts are run. Document the newly formalized commands from checkpoint 3.
   - **Risks / Edge Cases:** Ensure the documentation is clear and accurate to avoid confusion for other developers.

### 4. Behavior Changes

- **Backward-compatible:** No changes to the end-user application behavior.
- **Breaking (for developers):** The methods for executing scripts will change. Direct invocation (e.g., `python scripts/some_script.py`) will be replaced by formal console script commands (e.g., `doughub-some-script`). This is a breaking change for the developer workflow, which will be mitigated by updating `README.md`.

### 5. End-User Experience (UX)

- This refactoring has **no impact on the end-user experience**.
- The **developer experience (DX)** will be significantly improved by:
  - **Improved Clarity:** A more logical directory structure makes it easier to locate files.
  - **Consistency:** Formalizing scripts creates a consistent and discoverable way to perform common tasks.
  - **Reduced Clutter:** A clean root directory focuses attention on a few key files.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check . --fix` and `mypy src/ tests/` to enforce code quality and type safety after the file moves.
  - **Automated Testing:** `pytest` to ensure no regressions were introduced.
  - **Application Launch:** `python src/doughub/main.py` to confirm the application starts correctly.
  - **Script Execution:** Run each of the newly created console scripts (from checkpoint 3) to verify they work as expected.
- **Expected Results:**
  - All static analysis and test commands should exit with code 0 and report no new errors.
  - The test suite must pass completely.
  - The application's main window must appear without errors.
  - The consolidated scripts must execute successfully.
- **Manual QA Checklist:**
  - Review the `docs/` directory to ensure all files were moved correctly and the structure is logical.
  - Verify that the `README.md` is updated and the instructions for running the new script commands are clear and correct.
  - Delete the local repository and re-clone it, then follow the updated `README.md` to set up the project and run the main application and scripts. This validates the developer onboarding experience.
