### 1. Overview

- **Summary:** This plan begins the UI overhaul of the `DeckListPanel` by replacing the basic `QListWidget` with a more capable `ListWidget` from PySide6-Fluent-Widgets and implementing a custom item widget to display richer content for each deck.
- **Goals:**
  - Convert `deck_list` from `QListWidget` to `qfluentwidgets.ListWidget`.
  - Create a new, reusable `DeckListItemWidget` for displaying deck details (name, path, card count).
  - Modify the `DeckListPanel`'s `refresh` method to use this new custom widget for each item in the list.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/deck_list_panel.py`
  - **New Component:** A new `DeckListItemWidget` class will be created within this file.
- **Technology:** This is a **PySide6 + QFluentWidgets desktop app**.
- **Constraints:**
  - The new list widget MUST be `qfluentwidgets.ListWidget`.
  - The custom item widget should use standard `QWidget` layouts and `QLabel`s for now. The data for path and card count can be mocked with placeholder text until the data layer is updated.

### 3. Implementation Checkpoints

#### Checkpoint 1: Replace `QListWidget` and Create Custom Item Widget

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Import `ListWidget` from `qfluentwidgets` and other necessary Qt components (`QWidget`, `QHBoxLayout`, `QVBoxLayout`, `QLabel`).
  2.  In `DeckListPanel`, change the type of `self.deck_list` from `QListWidget` to `ListWidget`.
  3.  Above the `DeckListPanel` class, define a new class `DeckListItemWidget(QWidget)`.
  4.  In the `__init__` of `DeckListItemWidget`, create a layout and add labels for "Deck Name", "Deck Path", and "Card Count". Use placeholder text. It should have a main vertical layout, with the name on top, and the path/count on a second row.
  5.  The `DeckListItemWidget`'s constructor should accept `deck_name`, `deck_path`, and `card_count` and set the label texts accordingly.

#### Checkpoint 2: Integrate Custom Widget into `DeckListPanel`

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  Modify the `refresh` method in `DeckListPanel`.
  2.  Instead of `self.deck_list.addItems(deck_names)`, iterate through the `deck_names`.
  3.  For each `deck_name`, create an instance of `DeckListItemWidget`. For now, you can use the `deck_name` and hardcoded placeholders for path and count.
  4.  Create a `QListWidgetItem` for each deck.
  5.  Set the size hint of the `QListWidgetItem` to the size hint of your custom `DeckListItemWidget` instance (`item.setSizeHint(widget.sizeHint())`).
  6.  Add the item to the `ListWidget` (`self.deck_list.addItem(item)`).
  7.  Associate the custom widget with the item (`self.deck_list.setItemWidget(item, widget)`).
- **Risks / Edge Cases:** The `_on_deck_selection_changed` slot currently receives the item's text. This may need to be adapted if the custom widget changes how selection is handled. For now, the `QListWidgetItem` can still hold the deck name as its text.

### 4. Behavior Changes

- **Breaking Change:** The visual representation of the deck list will change from a simple text list to a list of custom widgets.
- The `currentTextChanged` signal from the list widget will still emit the deck name, so downstream functionality should not break.

### 5. End-User Experience (UX)

- **User Journey:** The user will see a list of decks that is more visually organized, with a clear separation of the deck's name from its (placeholder) metadata. This is the first step toward a richer, more informative UI.
- **Rationale:** This change establishes the foundation for a more complex and user-friendly filter panel. By using custom item widgets, we gain full control over the layout and styling of each deck entry, paving the way for future enhancements like checkboxes and custom icons.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application must launch, and the `DeckListPanel` on the left should now display a list of custom widgets, each with (at least) the deck name visible.
- **Manual QA Checklist:**
  - Launch the application.
  - Verify the deck list populates.
  - Verify that each item in the list is a custom widget showing the deck name and placeholder text for path/count.
  - Verify that clicking on a deck still correctly loads the deck's notes in the middle panel.
  - Check light/dark mode to ensure the new custom widgets adapt correctly.
