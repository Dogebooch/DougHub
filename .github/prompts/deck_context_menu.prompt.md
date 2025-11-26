### 1. Overview

- **Summary:** This plan implements a right-click context menu for items in the deck list panel, allowing users to perform common actions on a specific deck. The feature is based on a design prototype and will be implemented using native PySide6 and QFluentWidgets components.
- **Goals:**
  - Enable a right-click context menu on each deck in the `DeckListPanel`.
  - Provide actions: Rename, Options, Export, Custom Study, and Delete.
  - Connect each menu action to a placeholder slot that confirms the action via an `InfoBar`.
  - Ensure the menu's appearance and behavior are consistent with the QFluentWidgets design system.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/deck_list_panel.py`
  - **Relevant UI Component:** `QListWidget` within the `DeckListPanel` class.
- **Technology:** This is a **PySide6 + QFluentWidgets desktop app**. The provided web-based prototype (`FilterPanel.tsx`) will be used for semantic guidance only.
- **Constraints:**
  - The context menu MUST be a `qfluentwidgets.RoundMenu`.
  - Menu actions MUST use `qfluentwidgets.Action` and `qfluentwidgets.FluentIcon` for icons.
  - Feedback for placeholder actions SHOULD use `qfluentwidgets.InfoBar`.

### 3. Implementation Checkpoints

#### Checkpoint 1: Enable Custom Context Menu

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  In the `_setup_ui` method, set the `contextMenuPolicy` of `self.deck_list` to `Qt.ContextMenuPolicy.CustomContextMenu`.
  2.  In the `_connect_signals` method, connect the `customContextMenuRequested` signal of `self.deck_list` to a new slot, `self._show_context_menu`.
- **UI Translation Note:** This is the standard Qt mechanism for initiating a custom right-click menu, replacing the default browser behavior seen in the web prototype.

#### Checkpoint 2: Create the Context Menu Structure

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Import `RoundMenu` from `qfluentwidgets` and `QPoint` from `PyQt6.QtCore`.
  2.  Create the new method `_show_context_menu(self, pos: QPoint)`.
  3.  Inside this method, get the `QListWidgetItem` at the clicked position (`pos`). If no item is found, return early.
  4.  Get the deck name from the item's text.
  5.  Create a `RoundMenu` instance as the context menu.
- **Risks / Edge Cases:** Ensure the code gracefully handles a right-click on an empty area of the list widget where there is no item.

#### Checkpoint 3: Add Actions to the Menu

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Import `Action` from `qfluentwidgets` and `FluentIcon` from `qfluentwidgets`.
  2.  Inside `_show_context_menu`, add the following actions to the `RoundMenu`, mapping them from the prototype's intent:
      - "Rename" (`FluentIcon.EDIT`)
      - "Options" (`FluentIcon.SETTING`)
      - "Export" (`FluentIcon.SHARE`)
      - "Custom Study" (`FluentIcon.EDUCATION`)
  3.  Add a separator using `menu.addSeparator()`.
  4.  Add the "Delete" action (`FluentIcon.DELETE`). Give this action a distinct object name (e.g., `deleteAction`) for later styling.
- **UI Translation Note:** This directly translates the button list from the web prototype's JSX into a native `RoundMenu`. The icons are chosen from the `FluentIcon` enum to match the semantic meaning.

#### Checkpoint 4: Connect Actions to Placeholder Slots

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Create new placeholder methods: `_on_rename_deck`, `_on_deck_options`, `_on_export_deck`, `_on_custom_study`, and `_on_delete_deck`. Each should accept a `deck_name` string argument.
  2.  In `_show_context_menu`, use `functools.partial` to connect each action's `triggered` signal to its corresponding new slot, passing the `deck_name`. For example: `rename_action.triggered.connect(partial(self._on_rename_deck, deck_name))`.
- **Risks / Edge Cases:** Correctly capturing the `deck_name` for each menu invocation is critical. Using `partial` ensures the value is captured at the time of menu creation.

#### Checkpoint 5: Implement Placeholder Action Feedback

- **File(s):** `src/doughub/ui/deck_list_panel.py`, `src/doughub/ui/main_window.py`
- **Action:**
  1.  In `deck_list_panel.py`, modify the placeholder slots created in the previous step. Each slot should emit a signal (e.g., `show_info_bar = pyqtSignal(str, str)`).
  2.  In `main_window.py`, connect this new signal from the `DeckListPanel` instance to a method that creates and shows an `InfoBar`.
  3.  The `InfoBar` should display a message confirming the action, e.g., `InfoBar.success(title="Rename", content=f"Triggered rename for deck: {deck_name}", duration=3000, parent=self)`.
- **UI Translation Note:** This uses non-blocking `InfoBar` notifications, which is a better UX pattern for confirmation than modal dialogs, aligning with the project's UX principles.

### 4. Behavior Changes

- **New Behavior:** Right-clicking an item in the deck list will now open a custom context menu with five actions.
- **Backward-compatible:** Yes. This adds new functionality without altering existing interactions (left-click still selects a deck).

### 5. End-User Experience (UX)

- **User Journey:**
  1.  The user navigates to the view containing the `DeckListPanel`.
  2.  The user right-clicks on a specific deck in the list.
  3.  A fluent, rounded context menu appears at the cursor's position.
  4.  The user clicks an action, for example, "Rename".
  5.  The menu disappears, and a temporary, non-blocking `InfoBar` appears at the top of the main window confirming "Triggered rename for deck: [Deck Name]".
- **Rationale:** The use of `RoundMenu` and `InfoBar` from the QFluentWidgets library ensures the new feature is visually consistent with the existing application. The workflow is discoverable (a standard right-click) and provides immediate, non-intrusive feedback.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest` (No new tests are required for this UI-only plan, but existing tests must pass).
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - Static analysis and tests must pass with no errors.
  - The application must launch, and the deck list must populate correctly.
- **Manual QA Checklist:**
  - **Menu Appearance:**
    - Right-click a deck. Verify the `RoundMenu` appears.
    - Verify it contains the five actions ("Rename", "Options", "Export", "Custom Study", "Delete") with their corresponding icons.
    - Verify there is a separator above "Delete".
  - **Action Confirmation:**
    - Click "Rename". Verify an `InfoBar` appears with the correct title and content.
    - Repeat for all other actions, checking that the `InfoBar` content correctly identifies the action and the deck.
  - **No-Item Behavior:** Right-click in an empty area of the `DeckListPanel`. Verify that no context menu appears.
  - **Theme Behavior:** Switch between system light and dark modes and verify the menu's colors adapt correctly.
