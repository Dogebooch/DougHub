### 1. Overview

- **Summary:** This plan refactors the data layer for the `DeckBrowserView` to support a richer and more detailed table of notes. It involves updating the `Note` data model, the `NotesTableModel` that feeds the UI, and the `AnkiRepository` responsible for fetching the data from the Anki backend.
- **Goals:**
  - Update the `Note` data model in `src/doughub/models.py` to include fields required by the prototype (e.g., `reviews`, `ease`, `modified`).
  - Update `AnkiRepository` to fetch this new data from AnkiConnect.
  - Update `NotesTableModel` in `src/doughub/ui/deck_browser_view.py` to use the new data and expose the correct columns to the view.
- **Design Principle Note:** This plan uses PySide6 + QFluentWidgets and follows the DougHub UI/UX Algorithmic Design Standard. A well-structured data model is the foundation of a clear and performant UI.

### 2. Context & Constraints

- **Repo Mapping:**
  - **Files to Modify:** `src/doughub/models.py`, `src/doughub/anki_client/repository.py`, `src/doughub/ui/deck_browser_view.py`.
- **Technology:** This involves data modeling and API interaction with AnkiConnect, in addition to PySide6.
- **Prerequisites:** The `DeckBrowserView` and its `NotesTableModel` should exist as per the current codebase.

### 3. Implementation Checkpoints

#### Checkpoint 1: Update the `Note` Data Model

- **File(s):** `src/doughub/models.py`
- **Action:**
  1.  Locate the `Note` `TypedDict` or dataclass.
  2.  Add the following fields to the model, ensuring they are typed correctly:
      - `reviews: int`
      - `ease: float` (Ease is often represented as a percentage or factor)
      - `modified: str` (or a datetime object)
      - `lapses: int`
      - `interval: int`
      - `suspended: bool`
- **Risks / Edge Cases:** This change will cause type errors in any code that creates `Note` objects without these new fields. The `AnkiRepository` must be updated simultaneously.

#### Checkpoint 2: Update `AnkiRepository` to Fetch Detailed Note Info

- **File(s):** `src/doughub/anki_client/repository.py`
- **Action:**
  1.  Modify the `list_notes_in_deck` method. Currently, it likely calls `notesInfo` from AnkiConnect, which provides basic information.
  2.  To get the additional details (`reviews`, `ease`, etc.), you will need to first get the note IDs with `findNotes` and then call `cardsInfo` on the card IDs associated with those notes. A note can have multiple cards. For this implementation, assume one card per note for simplicity.
  3.  The workflow should be: `findNotes` -> get note IDs -> `notesInfo` (to get card IDs and existing info) -> `cardsInfo` (to get `reps` (reviews), `ease`, `ivl` (interval), `lapses`).
  4.  Consolidate the information from both API calls into the updated `Note` model object.
- **UI Translation Note:** The prototype has columns for "Reviews" and "Ease", which maps directly to the `reps` and `ease` factor data available from Anki cards.

#### Checkpoint 3: Update `NotesTableModel` for the View

- **File(s):** `src/doughub/ui/deck_browser_view.py`
- **Action:**
  1.  In `NotesTableModel`, update the `_headers` list to `["Front", "Reviews", "Ease", "Modified"]`.
  2.  Update the `columnCount` to reflect the new number of headers.
  3.  In the `data()` method, update the logic to handle the new columns:
      - Column 0 ("Front"): Return the content of the "Front" field from `note.fields`.
      - Column 1 ("Reviews"): Return `str(note.reviews)`.
      - Column 2 ("Ease"): Return a formatted string, e.g., `f"{(note.ease * 100):.0f}%"`.
      - Column 3 ("Modified"): Return a nicely formatted date string from `note.modified`.

### 4. Behavior Changes

- **Breaking Change:** The data model for notes is fundamentally changed.
- The `DeckBrowserView` table will now attempt to display different columns, which will be empty or cause errors until the UI rendering is also updated in the next prompt.
- The application will make more detailed API calls to AnkiConnect.

### 5. End-User Experience (UX)

- **User Journey:** There will be no immediate visual change for the end-user in this step, as the view itself isn't being updated yet. However, this is a critical backend step. When complete, the application will have access to the data needed to display a much more informative list of cards.
- **Rationale:** This refactoring decouples the data-fetching logic from the UI presentation. By enriching the data model first, we ensure the UI has everything it needs to render the complex table view, making the next UI-focused step cleaner.

### 6. Validation

- **Commands / Checks:**
  - **Static Analysis:** `ruff check .` and `mypy src/ tests/`
  - **Automated Testing:** `pytest`. Existing tests for the repository may need to be updated to reflect the new data model and API calls.
  - **Application Launch:** `python src/doughub/main.py`
- **Expected Results:**
  - All commands must pass.
  - The application should launch, and when a deck is clicked, the table in `DeckBrowserView` should now show the new headers: "Front", "Reviews", "Ease", "Modified". The rows will be populated with the new data. The formatting will be basic plain text for now.
- **Manual QA Checklist:**
  - Launch the application and connect to Anki.
  - Click on a deck with several cards.
  - Verify the table view updates and shows the four new columns.
  - Verify the data in the columns appears correct (e.g., numbers for reviews, percentages for ease).
  - Verify the "Front" column shows the front content of the card.
