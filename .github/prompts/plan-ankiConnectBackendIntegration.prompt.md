# Plan: AnkiConnect Backend Integration for PyQt UI

Build the foundational AnkiConnect API client and data models to enable deck exploration and card editing in your PyQt application. This establishes the HTTP contract with AnkiConnect and creates a clean, testable backend layer before GUI work.

## Steps

1. **Initialize project structure and dependencies** — Create `pyproject.toml` with PyQt6, requests, pytest; add `.gitignore`; establish `src/doughub/` package and `tests/` directory following instruction file conventions
2. **Implement `src/doughub/anki_client.py`** — Build `AnkiConnectClient` class with typed methods for essential actions: `get_version()`, `get_deck_names()`, `get_deck_names_and_ids()`, `find_notes()`, `get_notes_info()`, `get_model_names()`, `get_model_field_names()`, `add_note()`, `update_note_fields()`; include connection checking, error handling, and logging
3. **Define data models in `src/doughub/models.py`** — Create dataclasses/Pydantic models for `Deck`, `Note`, `Card`, `NoteType` (model) with proper type hints to represent AnkiConnect API responses; keep JSON serialization simple
4. **Write integration tests in `tests/test_anki_client.py`** — Test against real AnkiConnect instance (require Anki running); verify connectivity, deck listing, note search, CRUD operations; document test prerequisites (Anki must be open with AnkiConnect installed)
5. **Add configuration in `src/doughub/config.py`** — Define constants for AnkiConnect URL (`http://127.0.0.1:8765`), API version (6), timeouts; make overridable via environment variables for testing flexibility
6. **Create validation script `scripts/verify_ankiconnect.py`** — Standalone CLI tool to check AnkiConnect connectivity, list decks, and verify all required API actions work; useful for debugging and onboarding

## Further Considerations

1. **PyQt version choice?** — PyQt6 (modern, recommended) vs PyQt5 (more tutorials/examples)? PyQt6 is cleaner but PyQt5 has broader community support. **Recommendation: PyQt6** for long-term maintainability unless you have PyQt5 experience.
   User Response: We can use PyQt6. The only thing that I would want to keep in mind is if it will be easier for the AI to find more support for debugging and stuff for PyQt5, or you know, whatever, then we could utilize PyQt5. Otherwise, lets keep it most up to date with PyQt6.
2. **Async vs synchronous HTTP?** — AnkiConnect is localhost HTTP, so blocking requests are likely fine. Use `requests` (simple, synchronous) vs `httpx` (supports async if needed later)? **Recommendation: Start with `requests`** for simplicity; localhost calls are fast enough.
   User Response: Lets go with httpx then. I think it would be good to have the option to go async later on if we need to.
3. **Error handling granularity?** — Should the client raise custom exceptions (`AnkiConnectError`, `DeckNotFoundError`) vs generic `requests.RequestException`? **Recommendation: Custom exception hierarchy** for better error messages in the UI later.
   User Response: Custom exceptions sound good. That way we can have more specific error handling in the future if needed.
4. **Mock vs real tests?** — Integration tests require Anki running (slower, more setup). Also add unit tests with mocked HTTP responses? **Recommendation: Both** — unit tests with `responses`/`requests-mock` for fast CI; integration tests marked with `pytest.mark.integration` for local validation.
   User Response: I agree. We can have both types of tests to ensure robustness while keeping the CI fast. If Anki isn't running, please add a function that boots up Anki with AnkiConnect installed for testing purposes. The Profile to open is "DougHub_Testing_Suite".
