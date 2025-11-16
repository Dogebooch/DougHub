# DougHub UI - User Guide

## Overview

DougHub provides a clean, minimal PyQt6 interface for managing your Anki flashcards. The UI focuses on the essential operations: browsing decks, viewing notes, and editing cards.

## Getting Started

### Launch the Application

```bash
python -m doughub.main
```

or

```bash
python scripts/launch_ui.py
```

### Requirements

- Anki desktop application must be running
- AnkiConnect add-on must be installed (ID: 2055492159)

## Main Interface

The application window has three main areas:

```
┌─────────────────────────────────────────────────────┐
│ File                                    [Add Note]   │  ← Menu & Toolbar
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│  Deck 1      │                                       │
│  Deck 2      │                                       │
│  Deck 3      │         Deck Browser                 │  ← Main Content
│  ...         │              or                       │
│              │         Card Editor                   │
│              │                                       │
├──────────────┴──────────────────────────────────────┤
│ Status: Ready                                        │  ← Status Bar
└─────────────────────────────────────────────────────┘
```

### 1. Deck List (Left Sidebar)

- Shows all your Anki decks
- Click any deck to view its notes
- Automatically refreshes when the app starts

### 2. Deck Browser (Right Panel - View Mode)

When you select a deck, you'll see a table with:
- **Note ID**: Unique identifier for each note
- **Model**: The note type (e.g., "Basic", "Cloze")
- **Fields**: Preview of the note's content
- **Tags**: Associated tags

**Actions:**
- Double-click any row to edit that note
- Click "Add Note" to create a new note

### 3. Card Editor (Right Panel - Edit Mode)

The editor appears when you:
- Double-click a note in the browser (edit mode)
- Click the "Add Note" button (add mode)

**Components:**
- **Deck**: Select which deck to add the note to (disabled in edit mode)
- **Note Type**: Select the note type/model (disabled in edit mode)
- **Fields**: Dynamically generated based on the note type
  - Multi-line fields use text boxes
  - Single-line fields use input boxes
- **Buttons**:
  - **Save**: Creates the note (add mode) or updates it (edit mode)
  - **Cancel**: Returns to the deck browser without saving

## Common Workflows

### Browse a Deck

1. Click a deck name in the left sidebar
2. View all notes in the table
3. Notes are limited to 100 per deck for performance

### Edit a Note

1. Select a deck
2. Double-click the note you want to edit
3. Modify the field values
4. Click "Update" to save changes
5. You'll return to the deck browser

### Add a New Note

1. (Optional) Select the deck you want to add to
2. Click the "Add Note" button in the toolbar
3. Select the deck (if not already selected)
4. Select the note type
5. Fill in all fields
6. Click "Save"
7. You'll return to the deck browser

### Cancel Editing

- Click "Cancel" at any time to discard changes and return to the browser

## Status Bar

The status bar at the bottom shows:
- Current operation (e.g., "Loading deck: Default")
- Success messages (e.g., "Note 1234 saved successfully")
- Error messages (e.g., "Error loading note")

Messages disappear after 5 seconds.

## Keyboard Tips

- **Tab**: Move between fields in the editor
- **Alt+F**: Open File menu
- **Alt+F, X**: Exit the application

## Troubleshooting

### "Could not connect to AnkiConnect"

**Solution:**
1. Make sure Anki is running
2. Verify AnkiConnect add-on is installed
3. Restart Anki if needed

### Deck List is Empty

**Causes:**
- Anki has no decks
- AnkiConnect connection issue

**Solution:**
- Create a deck in Anki first
- Check the connection (see above)

### Field Layout is Wrong

The editor uses a simple heuristic for field types:
- Fields named "Back" or decks with ≤2 fields → Multi-line text box
- Other fields → Single-line input

This is by design for simplicity. Future versions may allow customization.

## Error Recovery

If you encounter an error:

1. Check the status bar for error details
2. Try the operation again
3. Verify Anki is running and responsive
4. Check the terminal/console for detailed error logs
5. Restart the application if needed

## Best Practices

- **Save Often**: Changes are only saved when you click "Save"
- **Check Status**: Watch the status bar for feedback on operations
- **Deck Limit**: If browsing large decks (>100 notes), only the first 100 will show
- **Field Values**: All fields must have values when creating notes (model dependent)

## Future Enhancements

Planned features:
- Search and filter within decks
- Advanced tag management
- Keyboard shortcuts
- Statistics and review data
- Batch operations

## Getting Help

- Check the README.md for technical details
- Review docs/UI_IMPLEMENTATION.md for architecture
- Report issues on the project's issue tracker
