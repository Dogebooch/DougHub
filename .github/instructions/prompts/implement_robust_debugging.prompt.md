### 1. Overview

- **Summary:** This plan implements a robust debugging and diagnostics framework for DougHub. The goal is to move beyond simple print statements and basic logging to a structured, contextual, and user-accessible system. This will involve enriching log messages with contextual data, creating a dedicated in-app diagnostics view, and improving the management and reporting of background service health (like Notesium and AnkiConnect).
- **Goals:**
  - Implement structured, contextual logging to make debugging easier.
  - Create a user-facing "Diagnostics" view to display system status and logs.
  - Improve the startup logic for background services to be more resilient and less noisy.
  - Centralize health checks for external services (Anki, Notesium) and reflect their status clearly in the UI.
  - Provide a simple mechanism for users to export logs and system information for bug reports.
- **Design Principle Note:**
  > “This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard.”

### 2. Context & Constraints

- **Repo Mapping:**
  - **Logging Configuration:** `src/doughub/config.py` and `src/doughub/main.py` will be modified to set up structured logging (e.g., using a custom formatter). A new `src/doughub/utils/logging.py` may be created.
  - **New UI Components:**
    - `src/doughub/ui/diagnostics_view.py`: A new view to display logs and system info.
    - A new "Diagnostics" or "Status" icon will be added to the main navigation interface in `src/doughub/ui/main_window.py`.
  - **Service Management:** Logic in `src/doughub/notebook/manager.py` and `src/doughub/anki_client/api.py` will be refactored for more robust health checks.
- **Technology:**
  - **Logging:** Python's built-in `logging` module, potentially with a custom `logging.Formatter` to add context.
  - **UI:** A `PlainTextViewer` or `TextEdit` within a new QFluentWidgets view. A `PrimaryPushButton` for exporting logs.
- **Constraints:**
  - The logging system should not introduce significant performance overhead in production. Log levels should be configurable.
  - The UI for diagnostics should be simple, clear, and follow the existing design system. It's a utility, not a primary feature.

### 3. Implementation Checkpoints

1.  **Checkpoint 1: Implement Structured Contextual Logging**
    - **File(s):** Modify `src/doughub/main.py`. Create `src/doughub/utils/logging.py`.
    - **Action:**
      1.  In `utils/logging.py`, create a custom `logging.Formatter` that can inject extra context (e.g., `module`, `function_name`, `request_id`).
      2.  In `main.py`, configure the root logger to use this new formatter.
      3.  Refactor key parts of the application (e.g., `anki_client`, `notebook.manager`) to pass extra context when logging. For example: `logger.info("Anki request failed", extra={"request_type": "deckNames"})`.
      4.  Configure `httpx` logging to be less verbose by default, setting its log level to `WARNING` instead of `INFO`.
    - **Risks / Edge Cases:** Overly verbose context can make logs unreadable. The context added should be high-signal information.

2.  **Checkpoint 2: Improve Notesium Server Startup Logic**
    - **File(s):** `src/doughub/notebook/manager.py`, `src/doughub/main.py`.
    - **Action:** Modify the `start_notesium_server` (or equivalent) function. Instead of trying to start the server and catching an error, it should first perform a lightweight health check (e.g., pinging `http://localhost:3030`). Only if the health check fails should it attempt to launch the server process. Update the log messages to clearly state the outcome: "Notesium already running" or "Starting new Notesium server process...".
    - **Risks / Edge Cases:** There could be a race condition where the server stops between the health check and the app deciding not to start it. The logic should be resilient to this.

3.  **Checkpoint 3: Create a UI Diagnostics View**
    - **File(s):** Create `src/doughub/ui/diagnostics_view.py`; Modify `src/doughub/ui/main_window.py`.
    - **Action:**
      1.  In `diagnostics_view.py`, create a new widget that contains a `TextEdit` (set to read-only) to display logs and a `PrimaryPushButton` labeled "Export Logs".
      2.  Create a custom logging handler that directs log records to this `TextEdit` widget.
      3.  In `main_window.py`, add a new navigation item (e.g., with a "bug" or "info" icon) that, when clicked, shows the `DiagnosticsView`.
      4.  Implement the "Export Logs" button functionality to save the content of the log view and basic system info (OS, Python version, app version) to a text file.
    - **UI Translation Note:** This view should be a standard `NavigationInterface` item. The log display should use a monospaced font for readability.

4.  **Checkpoint 4: Centralize Service Health Checks and UI Reporting**
    - **File(s):** Create `src/doughub/services.py`; Modify `src/doughub/ui/main_window.py`.
    - **Action:**
      1.  Create a new `services.py` module with a `HealthMonitor` class.
      2.  The `HealthMonitor` will be responsible for periodically checking the status of AnkiConnect and Notesium in the background. It should expose signals like `ankiStatusChanged(bool, str)` and `notesiumStatusChanged(bool, str)`.
      3.  In `main_window.py`, instantiate the `HealthMonitor`. Connect its signals to UI elements.
      4.  Add small status indicator icons (e.g., colored dots) to the status bar or a dedicated header area that reflect the health of these services (e.g., green for OK, red for down). Tooltips on these icons should provide more details from the health monitor.
    - **Risks / Edge Cases:** Background health checks should be infrequent to avoid spamming services with requests.

### 4. Behavior Changes

- **New Feature:** A "Diagnostics" view is now available in the main application navigation.
- **Improved UX:** The application provides clear, real-time visual feedback on the status of its background services (Anki, Notesium).
- **Improved UX:** The application startup is quieter and more intelligent, avoiding redundant process start-up attempts.
- **Backward-compatible:** All existing functionality remains, but is now more observable and robust.

### 5. End-User Experience (UX)

- When something goes wrong, the user is no longer reliant on just console output. They can navigate to the in-app Diagnostics view to see what's happening.
- The user can easily check if key integrations like Anki are connected and working via simple status icons in the main window.
- If a user needs to file a bug report, they can use the "Export Logs" button to generate a comprehensive, developer-friendly file, making the support process much more efficient.
- The overall impression is of a more professional and reliable application that is transparent about its internal state.

### 6. Validation

- **Commands / Checks:**
  - `pytest` to ensure no existing tests have been broken.
  - `python src/doughub/main.py` to launch the application for manual testing.
- **Expected Results:**
  - All automated tests pass.
  - The application starts up without the "Port already in use" warning if Notesium is already running.
  - The new Diagnostics navigation item is present and opens the correct view.
- **Manual QA Checklist:**
  - **Log Viewer:**
    - Open the Diagnostics view. Verify that log messages from application activity appear in the text view.
    - Click "Export Logs" and verify a `.txt` file is created with the logs and system information.
  - **Health Indicators:**
    - With Anki running, verify its status indicator is green.
    - Stop the AnkiConnect service and verify the indicator turns red and its tooltip shows an error.
    - Repeat the process for the Notesium server.
  - **Startup Logic:**
    - Ensure a Notesium server is running. Start the application and check the logs to confirm it *does not* try to start a new one.
    - Stop the Notesium server. Start the application and check the logs to confirm it *does* try to start a new one.