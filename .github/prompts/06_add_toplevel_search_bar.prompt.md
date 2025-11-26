### 1. Overview

- **Summary:** This final plan completes the main application frame's replication of the prototype. It adds the top-level global search bar and refines the three-column layout's proportions.
- **Goals:**
  - Add a prominent `SearchLineEdit` to the top of the main window.
  - Structure the top toolbar to hold the search bar and other global actions.
  - Adjust the initial proportions of the main `QSplitter` to better match the visual hierarchy of the prototype.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard. A global search bar provides a powerful, always-accessible entry point for users to find content, as seen in many modern applications.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/main_window.py`
- **Technology:** This is a **PySide6 + QFluentWidgets desktop app**.
- **Prerequisites:** Assumes the successful implementation of all previous prompts (01-05). The main window should already contain the three-panel `QSplitter`.

### 3. Implementation Checkpoints

#### Checkpoint 1: Implement the Top Toolbar and Search Bar

- **File(s):** `src/doughub/ui/main_window.py`
- **Action:**
  1.  Import `SearchLineEdit` from `qfluentwidgets`.
  2.  In `MainWindow._setup_ui`, locate the existing `toolbar` `QHBoxLayout`.
  3.  Instead of just an "Add Note" button, redesign this toolbar. You can create a `QWidget` with an `QHBoxLayout` to act as the main toolbar.
  4.  Add a `SearchLineEdit` to the layout. Give it a prominent stretch factor so it expands to fill available space. Set a placeholder text like "Search all notes...".
  5.  Keep the `add_note_button` but perhaps move it to the right side of the search bar, or style it as a `PrimaryPushButton`.
  6.  Connect the `textChanged` or `returnPressed` signal of the new search bar to a new placeholder slot in `MainWindow` (e.g., `_on_global_search_triggered`). This slot can simply log the search query for now.

#### Checkpoint 2: Refine Splitter Proportions

- **File(s):** `src/doughub/ui/main_window.py`
- **Action:**
  1.  In `MainWindow._setup_ui`, locate the line `self.splitter.setSizes([...])`.
  2.  The prototype shows the left filter panel as the smallest, the middle table as the largest, and the right preview panel as medium-sized.
  3.  Adjust the values in `setSizes` to better reflect this visual hierarchy. A good starting point might be `[250, 650, 400]` or a similar ratio that prioritizes the central content area. The exact values can be tweaked for the best feel.

### 4. Behavior Changes

- **New Behavior:**
  - A global search bar will now be present at the top of the application window.
  - The initial layout proportions of the three panels will be adjusted.

### 5. End-User Experience (UX)

- **User Journey:** The user will immediately see a familiar, powerful search bar at the top of the application, inviting them to search across their entire collection of notes. The adjusted layout proportions will naturally guide their eye towards the central `DeckBrowserView`, reinforcing its status as the primary content area.
- **Rationale:** The global search bar is a massive improvement to usability, offering a single point of entry for finding information. The layout adjustment, while subtle, improves the composition of the UI and helps guide user focus, following fundamental principles of visual hierarchy.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application must launch without errors.
- **Manual QA Checklist:**
  - **Search Bar:**
    - Verify that a search bar is visible at the top of the main window.
    - Verify it has appropriate placeholder text.
    - Type text into the search bar and press Enter. Check the application logs to confirm the placeholder slot was triggered and logged the query.
  - **Layout:**
    - On first launch, verify the three panels have their new initial sizes, with the center panel being the largest.
    - Verify the splitter still works correctly, allowing the user to resize the panels manually.
  - **Theme:** Check light/dark mode to ensure the new toolbar and search bar adapt correctly.
