# Repository Cleanup and Reorganization Plan

## 1. Overview

This plan details the steps to clean, organize, and document the `DougHub` repository. Now that the initial Tampermonkey extraction pipeline is functional, the goal is to improve the project's structure, maintainability, and developer experience by refactoring scripts, standardizing code quality, and consolidating documentation.

-   **Goal**: Create a well-organized, documented, and maintainable repository structure.
-   **Non-Goal**: This plan will not introduce major new application features. It is focused on refactoring and quality improvements.

## 2. Context and Constraints

-   **Repository State**: The project currently consists of a core Python application (`src/doughub`), a set of utility scripts (`scripts/`), a new Tampermonkey userscript (`tampermonkey/`), and various documentation files spread across the root, `docs/`, and `.github/` directories.
-   **Constraints**: All refactoring must preserve existing functionality. The way the Python application and the Tampermonkey script operate should not change from an end-user perspective, though the developer commands to run them may be updated for consistency.

## 3. Implementation Checkpoints (for Claude + Copilot)

### Checkpoint 1: Finalize Tampermonkey Script Documentation
1.  **Action**: Ensure the `tampermonkey/` directory contains a `README.md` file.
2.  **Details**: If the README does not exist, create it. It should explain the script's purpose, how to install it, and the necessary Anki/AnkiConnect setup. This aligns with the final step of the previous plan.
    -   **Use Zen `docgen`** on the `tampermonkey/` directory to generate a draft README if one is missing.

### Checkpoint 2: Refactor and Consolidate Python Scripts
The `scripts/` directory contains a mix of Python and PowerShell scripts. The Python scripts should be integrated into the main `doughub` package to make them more robust and discoverable.
1.  **Action**: Create a new CLI module: `src/doughub/cli.py`.
2.  **Action**: Move the logic from `scripts/health_check.py` into a function within `src/doughub/cli.py`. Use a library like `Typer` or `Click` (to be added to `pyproject.toml`) to expose it as a command.
    -   *Example with Typer*: `doughub health-check`
3.  **Action**: Move the logic from `scripts/launch_ui.py` into a function within `src/doughub/cli.py`.
    -   *Example with Typer*: `doughub launch-ui`
4.  **Action**: Update `pyproject.toml` to register the new CLI entry point.
    ```toml
    [project.scripts]
    doughub = "doughub.cli:app"
    ```
5.  **Action**: Delete the now-redundant Python scripts from the `scripts/` directory.
6.  **Action**: Create a `README.md` inside the `scripts/` directory to explain the purpose of the remaining PowerShell scripts (`demo_cli.ps1`, `verify_cli.ps1`).

### Checkpoint 3: Standardize Code Quality
1.  **Action**: Run a formatter across the entire Python codebase to ensure consistent style.
    -   **Command**: `ruff format .`
2.  **Action**: Run the linter to identify and fix quality issues.
    -   **Command**: `ruff check . --fix`
3.  **Action**: Run the type checker to find potential type-related bugs.
    -   **Command**: `mypy .`

### Checkpoint 4: Organize and Consolidate Documentation
1.  **Action**: Move `IMPLEMENTATION_SUMMARY.md` into the `docs/` directory.
2.  **Action**: Review all files in `docs/` and `.github/prompts/`. Archive or delete outdated planning documents. Move any persistent, high-level documentation from `.github/prompts/` into the `docs/` directory. The `.github/prompts/` folder should be for in-flight or very recent plans.
3.  **Action**: Update the main `README.md` to reflect the new, cleaned repository structure. It should provide a clear overview of the project and link to the more detailed documentation in the `docs/` directory and the new CLI commands.

## 4. Zen MCP Integration

-   **`analyze`**: Before starting, run `analyze` on the `scripts/` directory to understand the dependencies and complexity of the scripts being refactored.
-   **`codereview`**: After Checkpoint 2 (refactoring scripts into `cli.py`), run `codereview` on the diff to ensure all logic was transferred correctly and that the new CLI structure is sound.
-   **`precommit`**: After Checkpoint 3 (code quality), recommend adding a pre-commit hook to the project to automatically run `ruff format` and `ruff check` on future commits. This will maintain code quality automatically.

## 5. Behavior Changes

-   **Developer-Facing Changes**:
    -   Python scripts like `health_check.py` and `launch_ui.py` will no longer be run directly (e.g., `python scripts/health_check.py`).
    -   They will be replaced by integrated CLI commands, e.g., `doughub health-check` and `doughub launch-ui`. This provides a more professional and unified command-line interface.

## 6. End-User Experience

-   **Developer Experience**: The primary impact is on the developer. The repository will be significantly cleaner, better documented, and easier to navigate. Standardized commands and code quality will simplify future development and onboarding.
-   **End-User (Application)**: There will be no change for the end-users of the application or the Tampermonkey script.

## 7. Validation

1.  **CLI Validation**:
    -   After Checkpoint 2, run the new CLI commands to ensure they work correctly:
        -   `doughub health-check`
        -   `doughub launch-ui`
    -   Confirm their output and behavior are identical to the old scripts.
2.  **Code Quality Validation**:
    -   After Checkpoint 3, run the following commands and ensure they pass without errors:
        -   `ruff format . --check`
        -   `ruff check .`
        -   `mypy .`
3.  **Testing**:
    -   Run the project's full test suite to ensure no regressions were introduced during refactoring.
    -   **Command**: `pytest`
4.  **Documentation Validation**:
    -   Manually review the main `README.md` and the `docs/` directory to confirm they are organized, up-to-date, and easy to understand.