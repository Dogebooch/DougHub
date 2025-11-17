# Plan: Troubleshoot Notesium Integration

## 1. Overview

This plan outlines the steps to diagnose and resolve issues preventing the Notesium server from running and the Notesium instance from appearing in the main UI. The primary goal is to add enhanced logging and error reporting to pinpoint the failure's root cause.

- **Goals for this Plan:**
  - Determine why the Notesium subprocess is failing to start or remain running.
  - Identify why the `NotebookView` (the `QWebEngineView` hosting Notesium) is not visible or is failing to load.
  - Implement better error visibility in both the logs and the UI.
- **Non-Goals for this Plan:**
  - Implementing new features. This is strictly a debugging and validation effort.

## 2. Context and Constraints

- **This plan focuses on investigating the existing implementation.**
- **Relevant Files & Modules:**
  - `src/doughub/main.py` (Application entry point)
  - `src/doughub/notebook/manager.py` (Handles the Notesium subprocess)
  - `src/doughub/ui/main_window.py` (Main UI window, integrates the notebook view)
  - `src/doughub/ui/notebook_view.py` (The widget containing the `QWebEngineView`)
  - `src/doughub/config.py` (Contains configuration like port and notes directory)

## 3. Implementation Checkpoints

### Checkpoint 1: Enhance Logging in `NotesiumManager`

**Task:** Add detailed logging to the `NotesiumManager` to capture the subprocess launch details and any errors.

1.  **Edit `src/doughub/notebook/manager.py`:**
    - In the `start()` method, add a log statement to print the exact `notesium` command and arguments being executed.
    - In the `_health_check()` method, log the URL being checked.
    - **Crucially**, in the `except` block of the `start()` method, capture and log the `stdout` and `stderr` from the subprocess to see why it might be failing.
    - Add a log statement in the `stop()` method to confirm it is being called.

- **Zen MCP Integration:** Use `debug` to step through the `NotesiumManager.start()` method line-by-line to observe the subprocess creation and health check in real-time.

### Checkpoint 2: Add Diagnostic Logging to UI Components

**Task:** Add logging to the UI code to verify that the notebook view is being created, added to the layout, and loaded correctly.

1.  **Edit `src/doughub/ui/main_window.py`:**
    - In the `__init__` method, add a log statement immediately after `self.notebook_view = NotebookView(...)` is created.
    - Add a log statement confirming that `self.splitter.addWidget(self.notebook_view)` is called.
    - Log the URL being passed to `self.notebook_view.load_url()`.
2.  **Edit `src/doughub/ui/notebook_view.py`:**
    - In the `load_url()` method, log the URL that the `QWebEngineView` is attempting to load.
    - Connect a handler to the `self.web_view.loadFinished` signal. In this handler, log whether the load was successful (`ok=True`) or failed (`ok=False`).

- **Zen MCP Integration:** `codereview` the changes to ensure logging is added in the correct places without altering logic.

### Checkpoint 3: Implement Visible Error Reporting in the UI

**Task:** Modify the `NotebookView` to display a clear error message if it fails to load the Notesium URL.

1.  **Edit `src/doughub/ui/notebook_view.py`:**
    - Create a new method, `show_error_message(self, error_string: str)`. This method should use `self.web_view.setHtml()` to display a formatted HTML error message (e.g., a red box with the error text).
    - In the `loadFinished` signal handler from Checkpoint 2, if the load failed (`ok=False`), call `self.show_error_message()` with details about the failure.
    - In `main_window.py`, if `notesium_manager.start()` returns `False`, call a method on the `notebook_view` instance to display an initial error message indicating the server failed to start.

- **Zen MCP Integration:** `testgen` could be used to create a small test that simulates a failed URL load and verifies that `setHtml` is called with an error message.

## 4. Validation

- **Automated:** Existing tests should continue to pass. Run `ruff check .`, `mypy .`, and `pytest`.
- **Manual:**
  1.  **Clear Logs:** Clear any existing log files or console history.
  2.  **Run Application:** Execute `python src/doughub/main.py`.
  3.  **Inspect Logs:** Carefully review the console output. Look for the new log messages from `NotesiumManager` (the command, stdout/stderr) and the UI components (creation, URL loading). This is the most critical step.
  4.  **Inspect UI:**
      - If the notebook pane is blank, the logs should tell you why.
      - If the new error reporting works, the notebook pane itself should display a clear error message indicating what failed (e.g., "Notesium server failed to start" or "Failed to load URL: ...").
  5.  **Check Processes:** While the app is running, use your system's task manager to see if a `notesium` process was successfully launched.
