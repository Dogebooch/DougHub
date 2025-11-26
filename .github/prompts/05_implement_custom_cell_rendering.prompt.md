### 1. Overview

- **Summary:** This plan details the implementation of a custom cell renderer for the `DeckBrowserView`'s table. This is the key visual step to transform the plain text table into the rich, stylized list seen in the prototype, including rendering tags as "pills".
- **Goals:**
  - Replace the base `QTableView` with the `qfluentwidgets.TableWidget`.
  - Create a `QStyledItemDelegate` to take full control over cell painting.
  - Implement custom `paint` logic for the "Front" column to render the main text and a list of tags as styled pills below it.
  - Apply the custom delegate to the table view.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard. Custom delegates are the correct Qt pattern for creating high-performance, visually rich data views that go beyond simple text.

### 2. Context & Constraints

- **Repo Mapping:**
  - **File to Modify:** `src/doughub/ui/deck_browser_view.py`
  - **New Component:** A new `CardTableDelegate(QStyledItemDelegate)` class will be created.
- **Technology:** This is a PySide6 + QFluentWidgets desktop app. This task involves using the `QPainter` API for custom drawing.
- **Prerequisites:** Assumes successful implementation of prompt 04. The `NotesTableModel` must be providing the updated data structure, including a `tags` field on the `Note` object.

### 3. Implementation Checkpoints

#### Checkpoint 1: Switch to `TableWidget` and Create Delegate

- **File(s):** `src/doughub/ui/deck_browser_view.py`
- **Action:**
  1.  Import `TableWidget` from `qfluentwidgets`, and `QStyledItemDelegate`, `QStyle`, `QPainter` from the Qt modules.
  2.  In `DeckBrowserView._setup_ui`, change `self.table_view` from a `QTableView` to a `TableWidget`. `TableWidget` offers better integration with the fluent design system.
  3.  Define a new class `CardTableDelegate(QStyledItemDelegate)`.
  4.  In `DeckBrowserView._setup_ui`, instantiate this delegate and apply it to the table view using `self.table_view.setItemDelegate(self.delegate)`.

#### Checkpoint 2: Implement the Delegate's `paint` Method

- **File(s):** `src/doughub/ui/deck_browser_view.py`
- **Action:**
  1.  Inside `CardTableDelegate`, override the `paint(self, painter: QPainter, option: QStyle.QStyleOptionViewItem, index: QModelIndex)` method.
  2.  In the `paint` method, first, call the superclass's paint method to handle basic things like selection background: `super().paint(painter, option, index)`.
  3.  Get the `Note` object for the current `index` from the model.
  4.  Check `index.column()`. If the column is NOT 0 ("Front"), return and let the default paint handle it.
  5.  If the column IS 0, begin custom painting:
      - Save the painter state: `painter.save()`.
      - Set the pen color for text.
      - Draw the main "Front" text in the top part of the cell rectangle (`option.rect`).
      - Restore the painter state: `painter.restore()`.

#### Checkpoint 3: Implement Tag Pill Rendering

- **File(s):** `src/doughub/ui/deck_browser_view.py`
- **Action:**
  1.  Continuing in the `paint` method for column 0.
  2.  After drawing the "Front" text, calculate a new rectangle for the tags area in the bottom part of the cell.
  3.  Iterate through the `note.tags`. For each tag:
      - Save the painter state.
      - Set the brush color for the pill background (can use a color from the `qfluentwidgets` theme palette).
      - Set the pen color for the pill text.
      - Use `painter.drawRoundedRect(...)` to draw the pill shape.
      - Use `painter.drawText(...)` to draw the tag name inside the rounded rectangle.
      - Move the drawing position (`x` coordinate) for the next tag.
      - Restore the painter state.
  4.  To make this work, the row height will need to be increased. In `DeckBrowserView._setup_ui`, set a fixed row height on the table's vertical header: `self.table_view.verticalHeader().setDefaultSectionSize(60)`.

### 4. Behavior Changes

- **Breaking Change:** The appearance of the card/note table will be completely transformed from a plain text table to a rich, custom-drawn list that matches the prototype's design.

### 5. End-User Experience (UX)

- **User Journey:** When the user clicks a deck, they will now see a visually appealing list of cards. The separation of the card's front text from its metadata (tags) provides a much clearer visual hierarchy. The use of "pills" for tags is a modern UX pattern that makes the tags easily scannable and distinct from other text.
- **Rationale:** This is the most impactful visual change in the UI overhaul. It brings the application's core data display in line with modern design standards and the provided prototype, dramatically improving information clarity and aesthetic appeal.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application must launch.
- **Manual QA Checklist:**
  - Click on a deck.
  - Verify that the `DeckBrowserView` table now has a larger row height.
  - Verify that the "Front" column is custom-drawn.
  - Check that the front text is visible.
  - Check that tags are rendered below the front text as colored, rounded rectangles ("pills") with text inside.
  - Verify that selecting a row still works and highlights correctly.
  - Scroll the table to ensure the custom drawing is performant and doesn't produce visual artifacts.
  - Check light/dark mode to ensure the custom-drawn text and pill colors are legible in both themes.
