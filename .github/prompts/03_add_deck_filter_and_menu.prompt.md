### 1. Overview

- **Summary:** This plan adds crucial interactive features to the `DeckListPanel`: a local search filter to quickly find decks and a right-click context menu to perform actions on them.
- **Goals:**
  - Add a `SearchLineEdit` to the "Decks" section to filter the deck list in real-time.
  - Implement a `RoundMenu` context menu that appears on right-click.
  - Populate the menu with actions: Rename, Options, Export, Custom Study, and Delete.
  - Connect actions to placeholder slots that provide `InfoBar` feedback.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard. It enhances usability by providing standard, discoverable tools for searching and acting upon list items.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/deck_list_panel.py`
  - **Dependencies:** This plan depends on `src/doughub/ui/main_window.py` to display the `InfoBar` notifications.
- **Technology:** This is a **PySide6 + QFluentWidgets desktop app**.
- **Prerequisites:** Assumes successful implementation of prompts 01 and 02. The `DeckListPanel` must contain a `CollapsibleSection` holding a `ListWidget`.

### 3. Implementation Checkpoints

#### Checkpoint 1: Implement the Deck Filter

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Import `SearchLineEdit` from `qfluentwidgets`.
  2.  Create a new content widget for the "Decks" `CollapsibleSection` that uses a `QVBoxLayout`.
  3.  Instantiate `SearchLineEdit` and add it to the top of this layout. Add the `self.deck_list` widget below it.
  4.  Connect the `textChanged` signal of the `SearchLineEdit` to a new slot, `_on_filter_text_changed`.
  5.  In `_on_filter_text_changed`, iterate through all the items in `self.deck_list`. Get the deck name for each item (e.g., from the custom widget or item data) and set the item's visibility (`item.setHidden(True/False)`) based on whether the deck name contains the filter text.

#### Checkpoint 2: Implement Context Menu Creation

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Import `RoundMenu`, `Action`, `FluentIcon` from `qfluentwidgets`, and necessary Qt modules (`QPoint`, `Qt`).
  2.  In `_setup_ui` for `DeckListPanel`, set the `contextMenuPolicy` of `self.deck_list` to `Qt.ContextMenuPolicy.CustomContextMenu`.
  3.  Connect the `customContextMenuRequested` signal to a new slot: `_show_context_menu(self, pos: QPoint)`.
  4.  In `_show_context_menu`, get the `item` at the clicked position. If there is no item, return.
  5.  Retrieve the `deck_name` from the custom widget associated with the item.
  6.  Create a `RoundMenu` and add the actions: "Rename" (`FluentIcon.EDIT`), "Options" (`FluentIcon.SETTING`), "Export" (`FluentIcon.SHARE`), "Custom Study" (`FluentIcon.EDUCATION`), a separator, and "Delete" (`FluentIcon.DELETE`).

#### Checkpoint 3: Connect Menu Actions to Feedback

- **File(s):** `src/doughub/ui/deck_list_panel.py`, `src/doughub/ui/main_window.py`
- **Action:**
  1.  In `DeckListPanel`, define a new signal: `show_info_bar = pyqtSignal(str, str)`.
  2.  Create placeholder slots in `DeckListPanel` (e.g., `_on_rename_deck(self, deck_name: str)`). Each slot should emit `self.show_info_bar.emit(action_title, deck_name)`.
  3.  In `_show_context_menu`, use `functools.partial` to connect each menu action's `triggered` signal to its corresponding slot, passing the `deck_name`.
  4.  In `MainWindow`, find where `self.deck_list_panel` is instantiated. Connect `self.deck_list_panel.show_info_bar` to a new slot, `_show_deck_action_infobar`.
  5.  Implement `_show_deck_action_infobar` in `MainWindow` to create and display a success `InfoBar` with the appropriate title and content.

### 4. Behavior Changes

- **New Behavior:**
  - Users can type in a search box to filter the list of decks.
  - Right-clicking a deck opens a context menu with actions.
  - Clicking a menu action displays a confirmation message at the top of the window.

### 5. End-User Experience (UX)

- **User Journey:** The user can now quickly find a specific deck in a long list by typing its name. They can also right-click a deck to access a menu of relevant operations, a standard and expected desktop UX pattern. The `InfoBar` feedback confirms their action was received without interrupting their workflow.
- **Rationale:** Adding search and context menus significantly improves the efficiency and discoverability of deck management features, moving the panel from a simple display list to an interactive control surface.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application must launch without errors.
- **Manual QA Checklist:**
  - **Filter:**
    - Verify the search box is visible inside the "Decks" section.
    - Type text into the search box. Verify the list of decks filters in real-time.
    - Clear the search box. Verify the full list of decks reappears.
  - **Context Menu:**
    - Right-click a deck item. Verify the `RoundMenu` appears.
    - Verify all specified actions and the separator are present with icons.
    - Right-click in an empty area of the list. Verify no menu appears.
    - Click the "Rename" action. Verify a success `InfoBar` appears at the top of the main window with the correct deck name. Test other actions.
