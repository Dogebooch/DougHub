# Scripts Directory

This directory contains utility scripts for development, testing, and operational tasks.

## PowerShell Scripts

### `start_extraction_server.ps1`
Launches the Flask server for receiving data from the Tampermonkey userscript.

**Purpose**: Starts the extraction server that listens for HTTP POST requests from the browser extension, receives extracted question data, downloads images, and saves everything to the `extractions/` directory.

**Usage**:
```powershell
.\scripts\start_extraction_server.ps1
```

**Requirements**: 
- Virtual environment activated
- Flask and Flask-CORS installed
- Port 5000 available

### `demo_cli.ps1`
Demonstrates the DougHub CLI functionality with a complete workflow test.

**Purpose**: Runs a 7-step demo that:
1. Checks AnkiConnect connection
2. Lists all decks
3. Lists all note types
4. Shows fields for the Basic model
5. Lists notes from the Default deck
6. Creates a test note
7. Shows the created note details

**Usage**:
```powershell
.\scripts\demo_cli.ps1
```

**Requirements**: 
- DougHub CLI installed (`pip install -e .`)
- Anki running with AnkiConnect

### `verify_cli.ps1`
Quick verification that AnkiConnect is accessible and the CLI is working.

**Purpose**: Performs a basic connectivity test and lists decks and note types to confirm everything is configured correctly.

**Usage**:
```powershell
.\scripts\verify_cli.ps1
```

**Requirements**: 
- DougHub CLI installed
- Anki running with AnkiConnect

## Python Scripts

### `extraction_server.py`
Flask server for the Tampermonkey extraction workflow.

**Purpose**: HTTP server that receives extracted question data from the browser, downloads associated images, and saves structured JSON and HTML files.

**Usage**: Use the PowerShell wrapper script instead:
```powershell
.\scripts\start_extraction_server.ps1
```

Or run directly:
```bash
python scripts/extraction_server.py
```

### `verify_ankiconnect.py`
Comprehensive AnkiConnect verification tool.

**Purpose**: Tests all major AnkiConnect operations to verify the API is working correctly. Includes options for auto-launching Anki if not running.

**Usage**:
```bash
python scripts/verify_ankiconnect.py
python scripts/verify_ankiconnect.py --auto-launch
```

## Migrated to CLI

The following scripts have been migrated to the unified `doughub` CLI:

- ~~`health_check.py`~~ → Use `doughub health-check` instead
- ~~`launch_ui.py`~~ → Use `doughub launch-ui` instead

## Notes

- PowerShell scripts are Windows-specific wrappers that provide a better user experience with colored output and error handling.
- Python scripts are cross-platform and can be run directly or wrapped by PowerShell.
- For new functionality, prefer adding commands to the `doughub` CLI rather than creating new standalone scripts.
