### 1. Overview

- **Summary:** This plan introduces a reusable `CollapsibleSection` widget to organize the `DeckListPanel`. This will create an accordion-style layout, matching the prototype and allowing users to show or hide different filtering sections (Decks, Card State, Tags).
- **Goals:**
  - Create a generic, reusable `CollapsibleSection` widget.
  - Refactor the `DeckListPanel` to use `CollapsibleSection` for the main "Decks" list.
  - Add placeholder `CollapsibleSection` widgets for "Card State" and "Saved Filters" to complete the layout structure.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard. It implements the "proximity grouping" Gestalt principle by chunking related controls into collapsible areas.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/deck_list_panel.py`
  - **New Component:** A new `CollapsibleSection` class will be created, likely within `deck_list_panel.py` for now.
- **Technology:** This is a **PySide6 + QFluentWidgets desktop app**.
- **Prerequisites:** This plan assumes the successful implementation of `01_refactor_deck_list_panel_content.prompt.md`, specifically the existence of the `ListWidget` with custom `DeckListItemWidget` items.

### 3. Implementation Checkpoints

#### Checkpoint 1: Create the `CollapsibleSection` Widget

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  At the top of the file, define a new class `CollapsibleSection(QWidget)`.
  2.  The `__init__` should accept a `title: str`, an `icon` (e.g., a `FluentIcon` enum value), and a `content_widget: QWidget`.
  3.  Create a main `QVBoxLayout` for the section.
  4.  Create a header `QWidget` with an `QHBoxLayout`. This header will contain an `IconWidget` (for the icon), a `SubsetTitleLabel` (for the title), and a `ToolButton` with an arrow icon (`FluentIcon.CHEVRON_DOWN`).
  5.  Add the header and the `content_widget` to the main layout.
  6.  Connect the header's click event (or the tool button's click) to a `_toggle_visibility` slot. This slot will show/hide the `content_widget`. The arrow icon should also change direction (e.g., `FluentIcon.CHEVRON_RIGHT`).

#### Checkpoint 2: Integrate `CollapsibleSection` into `DeckListPanel`

- **File(s):** `src/doughub/ui/deck_list_panel.py`
- **Action:**
  1.  In `DeckListPanel._setup_ui`, change the main layout from a simple `QVBoxLayout` that just holds the list to one that will hold the collapsible sections.
  2.  Instantiate a `CollapsibleSection` for "Decks", passing "Decks" as the title, `FluentIcon.FOLDER` as the icon, and the existing `self.deck_list` as the content widget.
  3.  Instantiate placeholder `CollapsibleSection` widgets for "Saved Filters" (Icon: `FluentIcon.STAR`) and "Card State" (Icon: `FluentIcon.CLOCK`). For their content widgets, you can use a simple `QLabel("Coming soon...")` for now.
  4.  Add these `CollapsibleSection` instances to the main layout of `DeckListPanel`.

### 4. Behavior Changes

- The `DeckListPanel` will now have a structured, accordion-style layout.
- The list of decks will be inside a "Decks" section that can be collapsed and expanded by the user.
- Placeholder sections for "Saved Filters" and "Card State" will be visible.

### 5. End-User Experience (UX)

- **User Journey:** The user will now see a more organized side panel. They can collapse the deck list to hide it, reducing visual clutter if they are focused on other parts of the UI. This introduces a clear visual hierarchy to the filtering controls.
- **Rationale:** This change improves the scalability of the filter panel. As more filtering options are added, the collapsible sections prevent the UI from becoming overwhelming. This follows the design principle of progressive disclosure.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application must launch.
- **Manual QA Checklist:**
  - Verify the `DeckListPanel` now shows collapsible sections for "Decks", "Saved Filters", and "Card State".
  - Verify the "Decks" section is open by default and contains the list of decks.
  - Click the header of the "Decks" section. Verify the list of decks hides and the arrow icon changes direction. Click again to verify it reappears.
  - Verify the "Saved Filters" and "Card State" sections are present with their placeholder content.
  - Check light/dark mode to ensure the new section headers and layouts adapt correctly.
