# Plan: Robust Notesium Server Integration

## 1. Overview

This plan addresses the failure of the Notesium server to start within the DougHub application. The current implementation relies on `npx` to download and run Notesium on-the-fly, which introduces an unmanaged dependency on Node.js and npm being installed on the user's system.

The goal is to make the Notesium integration self-contained and reliable by vendoring it as a development dependency and improving the process management logic.

**Goals:**

- Eliminate the runtime dependency on a system-wide `npx`.
- Manage the `notesium` package version explicitly within the project.
- Improve error handling and user feedback in `NotesiumManager`.
- Provide a clear CLI command for setting up this dependency.

**Non-Goals:**

- Forking or modifying the Notesium source code.
- Changing the core purpose of the `notebook` feature.

## 2. Context and Constraints

- **Relevant Files:**
  - `p:\Python Projects\DougHub\src\doughub\notebook\manager.py`: The `NotesiumManager` class that handles the server lifecycle.
  - `p:\Python Projects\DougHub\src\doughub\main.py`: The main application entry point that starts the manager.
  - `p:\Python Projects\DougHub\src\doughub\cli.py`: The Typer-based CLI where new commands will be added.
  - `p:\Python Projects\DougHub\pyproject.toml`: (This file will be created) To manage project metadata and dependencies.
- **Constraints:**
  - The solution should work on Windows, as suggested by the file paths.
  - The changes should not break existing functionality for users who do not use the notebook features.
  - The dependency on Node.js should be made explicit and manageable.

## 3. Implementation Checkpoints (for Claude + Copilot)

### Checkpoint 1: Create `pyproject.toml` and Add `package.json`

First, we need to formalize the project structure and add a `package.json` to manage the `notesium` dependency.

**Edits:**

1. **Create `p:\Python Projects\DougHub\pyproject.toml`:**

   - Define the project metadata (`name`, `version`).
   - Add a `[tool.poetry.scripts]` or similar section to define the `doughub` entry point if one doesn't exist.
2. **Create `p:\Python Projects\DougHub\package.json`:**

   - Add `notesium` as a `devDependency`. This pins the version and makes the dependency explicit.

   ```json
   {
     "name": "doughub-notebook",
     "version": "0.1.0",
     "private": true,
     "description": "Node.js dependencies for DougHub notebook features.",
     "devDependencies": {
       "notesium": "^0.2.1"
     }
   }
   ```

### Checkpoint 2: Update `NotesiumManager` to Use Local Dependency

Modify `NotesiumManager` to run Notesium from the local `node_modules` directory instead of using `npx`. This removes the dependency on a global `npx` and ensures the correct version is used.

**Edits:**

- **File:** `p:\Python Projects\DougHub\src\doughub\notebook\manager.py`
- **Changes:**
  - Update the `start` method to build a path to the local `notesium` executable.
  - The command should now point to `./node_modules/.bin/notesium`.
  - Improve error handling to give a more specific message if `node_modules` or the executable is missing, guiding the user to run the new setup command.

### Checkpoint 3: Add a CLI Command for Notebook Setup

Create a new command in `doughub/cli.py` to automate the setup process for the notebook feature. This command will install the Node.js dependencies.

**Edits:**

- **File:** `p:\Python Projects\DougHub\src\doughub\cli.py`
- **Changes:**
  - Add a new command `notebook setup` to the `notebook_app` Typer group.
  - This command will execute `npm install` in the project root.
  - It should first check if `npm` is available in the system's PATH and provide a helpful error message if it's not.

## 4. Zen MCP Integration

- **After Checkpoint 2:**
  - **`codereview`**: Run `zen codereview` on `p:\Python Projects\DougHub\src\doughub\notebook\manager.py` to ensure the new command construction is safe and the error handling is robust.
- **After Checkpoint 3:**
  - **`testgen`**: Use `zen testgen` to create unit tests for the new `notebook setup` CLI command. Mock the `subprocess.run` call to verify it's called with `npm install` and that it correctly handles the case where `npm` is not found.
- **Final Step:**
  - **`precommit`**: Run `zen precommit` to check the entire changeset for style issues, static analysis errors, and to run all tests.

## 5. Behavior Changes

- **Dependency Management:** The project now explicitly depends on Node.js and `npm` for the optional notebook functionality. This was previously an implicit dependency.
- **Startup Command:** The command to start Notesium changes from `npx -y notesium ...` to a direct call to the executable in `node_modules`.
- **New Setup Step:** Users wishing to use the notebook feature must now run `doughub notebook setup` once after cloning the repository.

## 6. End-user Experience

- **Clarity:** The failure mode is now much clearer. If Notesium fails to start, the error message will point to the missing `node_modules` and instruct the user to run `doughub notebook setup`.
- **Reliability:** By pinning the `notesium` version, we ensure that all developers and users run the exact same version, preventing unexpected issues from upstream updates.
- **Onboarding:** The new `doughub notebook setup` command simplifies the setup process for developers and contributors.

## 7. Validation

1. **Delete `node_modules` directory** if it exists.
2. **Run the application:** `python -m doughub.main`.
   - **Expected:** The application should start, but the logs should show a clear warning that Notesium failed to start and that `doughub notebook setup` should be run.
3. **Run the new setup command:** `doughub notebook setup`.
   - **Expected:** The command should print "Installing notebook dependencies..." and successfully run `npm install`. A `node_modules` directory should appear.
4. **Run the application again:** `python -m doughub.main`.
   - **Expected:** The application and the Notesium server should start successfully. The logs should indicate "Notesium started successfully".
5. **Manual Check:** Open a web browser to `http://localhost:3030` (or the configured port) to confirm the Notesium UI loads.
6. **Run automated tests:** `pytest` to ensure no existing tests were broken.
