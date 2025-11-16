# AnkiConnect Validation Pipeline

This document describes the 4-stage validation pipeline for testing the AnkiConnect backend integration. The pipeline verifies the contract between DougHub and AnkiConnect from local invariants through negative-path robustness checks.

## Overview

The validation pipeline consists of 4 stages:

- **Stage 0**: Local invariants (no Anki required)
- **Stage 1**: Handshake with live AnkiConnect
- **Stage 2**: Core contract checks for required actions
- **Stage 3**: Negative-path and robustness checks

Each stage builds on the previous one, progressively verifying more complex interactions with AnkiConnect.

## Prerequisites

### Stage 0
- Python 3.10+
- Project dependencies installed (`pip install -e ".[dev]"`)

### Stages 1-3
- All Stage 0 prerequisites
- Anki installed and accessible
- AnkiConnect add-on installed (code: `2055492159`)
- Profile `DougHub_Testing_Suite` configured (or set `ANKI_TEST_PROFILE` environment variable)

## Running the Tests

### Quick Start

Run all stages using the health check script:

```bash
python scripts/health_check.py
```

Run a specific stage:

```bash
python scripts/health_check.py --stage 0
python scripts/health_check.py --stage 1
```

Run multiple stages:

```bash
python scripts/health_check.py --stage 1 --stage 2
```

### Using pytest Directly

Run all tests for a stage:

```bash
# Stage 0 - No Anki required
pytest -v -m contract_stage0

# Stage 1 - Requires Anki
pytest -v -m contract_stage1

# Stage 2 - Requires Anki
pytest -v -m contract_stage2

# Stage 3 - Requires Anki + mocked tests
pytest -v -m contract_stage3
```

Run all contract tests:

```bash
pytest -v -m "contract_stage0 or contract_stage1 or contract_stage2 or contract_stage3"
```

Exclude integration tests (runs Stage 0 + non-integration Stage 3 tests):

```bash
pytest -v -m "not integration"
```

## Stage Details

### Stage 0: Local Invariants

**Location**: `tests/test_contract_stage0.py`

**Requirements**: No Anki needed

**What it tests**:
- Module imports succeed
- Configuration values are correct (`ANKICONNECT_URL`, `ANKICONNECT_VERSION`)
- Response parsing follows AnkiConnect contract:
  - `{"result": X, "error": null}` → returns `X`
  - `{"result": null, "error": "msg"}` → raises `AnkiConnectAPIError`
  - Missing `error` field → raises validation error
  - Malformed JSON → raises parse error

**Why it matters**: Validates local contract and configuration without external dependencies.

**Running**:
```bash
pytest -v -m contract_stage0
```

### Stage 1: Handshake with Live AnkiConnect

**Location**: `tests/test_contract_stage1.py`

**Requirements**: Anki running with AnkiConnect

**What it tests**:
- `version` returns integer 1-6
- `requestPermission` returns structured response (if supported)
- `deckNames` returns `list[str]` with `error == null`
- Full handshake sequence completes without errors

**Why it matters**: Verifies basic connectivity and protocol compatibility before testing complex operations.

**Running**:
```bash
pytest -v -m contract_stage1
```

If handshake fails, all Stage 1 tests are skipped with a clear message.

### Stage 2: Core Contract Checks

**Location**: `tests/test_contract_stage2.py`

**Requirements**: Anki running with AnkiConnect + test deck

**What it tests**:
- **Deck and model listing**:
  - `deckNames` → `list[str]`
  - `modelNames` → `list[str]`
  - `modelFieldNames("Basic")` → ordered `list[str]`
- **Note finding and retrieval**:
  - `findNotes(query)` → `list[int]`
  - `notesInfo(note_ids)` validates structure (noteId, modelName, fields, tags)
- **Note creation**:
  - `addNote` → integer ID
  - Verify created note via `notesInfo`
- **Note updating**:
  - `updateNoteFields` changes specified fields
  - Other fields remain unchanged
- **Full integration**: findNotes → notesInfo pipeline

**Why it matters**: Proves that all required actions work correctly with proper data structures.

**Running**:
```bash
pytest -v -m contract_stage2
```

**Test deck**: Uses `DougHub_Testing` deck (auto-created if missing).

**Cleanup**: Tests register created notes for automatic cleanup via `register_note_for_cleanup()`.

### Stage 3: Negative-Path and Robustness

**Location**: `tests/test_contract_stage3.py`

**Requirements**: Anki running (integration tests) or just respx (unit tests)

**What it tests**:
- **Invalid action names**:
  - Returns HTTP 200 with `error` field
  - Error message includes "unsupported" or similar
- **Invalid parameters**:
  - `modelFieldNames("NonExistentModel")` → `ModelNotFoundError`
  - `addNote` with missing field → `InvalidNoteError`
  - `addNote` with bad deck → `DeckNotFoundError`
  - `addNote` with bad model → `ModelNotFoundError`
- **Error context preservation**:
  - All errors include original action name
- **Transport-level robustness**:
  - Corrupted JSON → clear parse error
  - Non-JSON response → clear parse error
  - Empty response → clear parse error
  - No internal tracebacks leak to callers

**Why it matters**: Ensures graceful error handling and helpful error messages for debugging.

**Running**:
```bash
pytest -v -m contract_stage3
```

**Mixed mode**: Integration tests require Anki; unit tests use mocked responses.

## Health Check Script

The `scripts/health_check.py` script provides a convenient way to run the validation pipeline with colorized output and exit codes suitable for CI/CD.

### Usage

```bash
# Run all stages
python scripts/health_check.py

# Run specific stage(s)
python scripts/health_check.py --stage 0
python scripts/health_check.py --stage 1 --stage 2

# Stop at first failure
python scripts/health_check.py --fail-fast

# Auto-launch Anki if not running (Stages 1-3)
python scripts/health_check.py --auto-launch
```

### Exit Codes

- `0`: All requested stages passed
- `1`: One or more stages failed
- `2`: Invalid arguments or setup error

### Output

The script provides colorized output with symbols:
- ✓ Success
- ✗ Failure
- ℹ Info

## Test Fixtures and Helpers

### Fixtures (defined in `tests/conftest.py`)

- **`anki_manager`** (session-scoped): Manages Anki process lifecycle, auto-launches if needed
- **`test_deck_manager`** (session-scoped): Ensures `DougHub_Testing` deck exists
- **`integration_client`** (function-scoped): Provides AnkiConnect client, skips if unavailable
- **`track_test_notes`** (autouse): Automatically cleans up notes created during tests

### Helper Functions

- **`register_note_for_cleanup(note_id)`**: Mark a note for deletion after test
- **`assert_valid_note_structure(note_dict)`**: Validate note structure from AnkiConnect

### Example Usage

```python
@pytest.mark.integration
def test_my_feature(integration_client, test_deck_manager):
    """Test that requires Anki and a test deck."""
    client = integration_client
    test_deck = test_deck_manager
    
    # Create a note
    note_id = client.add_note(
        deck_name=test_deck,
        model_name="Basic",
        fields={"Front": "Q", "Back": "A"},
    )
    
    # Register for cleanup
    register_note_for_cleanup(note_id)
    
    # Test operations...
```

## Configuration

Configure via environment variables:

```bash
# AnkiConnect settings
export ANKICONNECT_URL="http://127.0.0.1:8765"
export ANKICONNECT_VERSION="6"
export ANKICONNECT_TIMEOUT="10.0"

# Anki application settings
export ANKI_EXECUTABLE="anki"  # or full path on Windows
export ANKI_TEST_PROFILE="DougHub_Testing_Suite"

# Testing configuration
export ENABLE_ANKI_AUTO_LAUNCH="true"  # Auto-launch Anki for tests
```

## CI/CD Integration

### GitHub Actions (Recommended)

Run Stage 0 in CI (no Anki required):

```yaml
name: Contract Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: python scripts/health_check.py --stage 0
```

### Local Pre-commit

Run Stage 0 as a quick pre-commit check:

```bash
# In .git/hooks/pre-commit
python scripts/health_check.py --stage 0 --fail-fast
```

### Manual Validation

Before deploying or releasing, run all stages locally:

```bash
# Ensure Anki is running, then:
python scripts/health_check.py
```

## Troubleshooting

### Anki Not Found

**Error**: `Anki executable 'anki' not found`

**Solution**: Set `ANKI_EXECUTABLE` environment variable:

```bash
# Windows
$env:ANKI_EXECUTABLE = "C:\Program Files\Anki\anki.exe"

# macOS
export ANKI_EXECUTABLE="/Applications/Anki.app/Contents/MacOS/Anki"

# Linux
export ANKI_EXECUTABLE="/usr/bin/anki"
```

### AnkiConnect Not Installed

**Error**: `AnkiConnect handshake failed`

**Solution**:
1. Open Anki
2. Go to Tools → Add-ons → Get Add-ons
3. Enter code: `2055492159`
4. Restart Anki

### Profile Not Found

**Error**: `Profile 'DougHub_Testing_Suite' not found`

**Solution**:
1. Open Anki
2. File → Switch Profile → Add
3. Create profile named `DougHub_Testing_Suite`

Or set a different profile:

```bash
export ANKI_TEST_PROFILE="MyProfile"
```

### Tests Hanging

**Symptom**: Tests never complete, hang during Anki launch

**Solution**:
- Launch Anki manually before running tests
- Increase timeout: `export ANKICONNECT_TIMEOUT="30.0"`
- Disable auto-launch: `export ENABLE_ANKI_AUTO_LAUNCH="false"`

### Permission Denied

**Error**: `requestPermission returned "denied"`

**Solution**: In Anki's AnkiConnect settings, enable permissions for localhost.

## Best Practices

1. **Run Stage 0 frequently**: Fast, no setup, catches config/contract issues early
2. **Run Stages 1-3 before commits**: Ensure full integration works
3. **Use `--fail-fast` during development**: Stop at first failure for quick feedback
4. **Register notes for cleanup**: Always call `register_note_for_cleanup()` after creating notes
5. **Use test deck**: Never test against production decks
6. **Check CI logs**: Stage 0 should always pass in CI

## Future Enhancements

Potential improvements to the validation pipeline:

- [ ] Performance benchmarks in Stage 2 (response time assertions)
- [ ] Parallel test execution with `pytest-xdist`
- [ ] Docker-based Anki for CI (headless testing)
- [ ] Test data factories for consistent note creation
- [ ] Retry logic for flaky network operations
- [ ] Coverage reporting for contract tests
- [ ] Unique test deck per session for complete isolation
- [ ] Automatic error report generation

## References

- [AnkiConnect Documentation](https://foosoft.net/projects/anki-connect/)
- [AnkiConnect API Reference](https://foosoft.net/projects/anki-connect/#supported-actions)
- [Anki Documentation](https://docs.ankiweb.net/)
- [pytest Documentation](https://docs.pytest.org/)
