# Validation Pipeline - Quick Reference

## Running Tests

### Health Check Script (Recommended)
```bash
# Run all stages
python scripts/health_check.py

# Run Stage 0 only (no Anki needed)
python scripts/health_check.py --stage 0

# Run multiple specific stages
python scripts/health_check.py --stage 0 --stage 1

# Stop at first failure
python scripts/health_check.py --fail-fast

# Auto-launch Anki if needed
python scripts/health_check.py --auto-launch
```

### Using pytest Directly
```bash
# Run by stage marker
pytest -v -m contract_stage0  # Stage 0
pytest -v -m contract_stage1  # Stage 1
pytest -v -m contract_stage2  # Stage 2
pytest -v -m contract_stage3  # Stage 3

# Run specific test file
pytest -v tests/test_contract_stage0.py

# Run all contract tests
pytest -v -m "contract_stage0 or contract_stage1 or contract_stage2 or contract_stage3"

# Run all tests except integration
pytest -v -m "not integration"
```

## Stage Summary

| Stage | Tests | Requires Anki | Description |
|-------|-------|---------------|-------------|
| **0** | 8 | ❌ No | Local invariants, config checks, response parsing |
| **1** | 4 | ✅ Yes | Handshake, version check, basic connectivity |
| **2** | 8 | ✅ Yes | Core actions: decks, models, notes (CRUD) |
| **3** | 9 | ⚡ Mixed | Error handling (6 need Anki, 3 mocked) |

## Test Files

```
tests/
├── conftest.py                  # Fixtures and helpers
├── test_contract_stage0.py      # Stage 0: Local invariants
├── test_contract_stage1.py      # Stage 1: Handshake
├── test_contract_stage2.py      # Stage 2: Core contract
└── test_contract_stage3.py      # Stage 3: Negative paths
```

## Common Commands

### Pre-commit Check
```bash
python scripts/health_check.py --stage 0 --fail-fast
```

### Full Local Validation (requires Anki)
```bash
python scripts/health_check.py
```

### CI/CD (no Anki)
```bash
pytest -v -m "not integration"
```

### Debug Specific Stage
```bash
pytest -v -s -m contract_stage0  # -s shows print statements
```

## Exit Codes

- `0` = All tests passed ✅
- `1` = Some tests failed ❌
- `2` = Setup error ⚠️

## Key Fixtures

- `anki_manager` - Manages Anki process, auto-launches if needed
- `test_deck_manager` - Ensures test deck exists
- `integration_client` - Provides AnkiConnect client
- `track_test_notes` - Auto-cleanup of created notes

## Helper Functions

```python
# Mark note for cleanup after test
register_note_for_cleanup(note_id)

# Validate note structure from API
assert_valid_note_structure(note_dict)
```

## Troubleshooting

### Anki Not Found
```bash
# Windows
$env:ANKI_EXECUTABLE = "C:\Program Files\Anki\anki.exe"

# macOS
export ANKI_EXECUTABLE="/Applications/Anki.app/Contents/MacOS/Anki"

# Linux
export ANKI_EXECUTABLE="/usr/bin/anki"
```

### Use Different Profile
```bash
export ANKI_TEST_PROFILE="MyProfile"
```

### Disable Auto-launch
```bash
export ENABLE_ANKI_AUTO_LAUNCH="false"
```

## Documentation

- **Full Documentation**: `docs/VALIDATION_PIPELINE.md`
- **Implementation Summary**: `docs/VALIDATION_IMPLEMENTATION_SUMMARY.md`
- **Main README**: `README.md`
