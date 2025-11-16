# Plan: Refactor to 4-layer backend architecture

Reorganize the monolithic `anki_client.py` into a clean layered architecture under `src/doughub/anki_client/` with transport → API → repository → CLI separation. This refactoring maintains all existing functionality and test compatibility while creating clear boundaries between HTTP communication, AnkiConnect protocol, business operations, and CLI interface.

## Steps

1. **Create `anki_client/transport.py`** — Extract HTTP client from `anki_client.py`::`_invoke` into `AnkiConnectTransport` class with single `invoke(action, params)` method, connection management (`check_connection`, `get_version`, `close`), and basic HTTP error handling (raise `AnkiConnectConnectionError` for httpx failures, `AnkiConnectAPIError` for non-null error responses)

2. **Create `anki_client/api.py`** — Build `AnkiConnectAPI` class wrapping `AnkiConnectTransport` with typed methods for all 11 existing actions (`get_deck_names`, `get_decks_with_ids`, `get_model_names`, `get_model_field_names`, `get_model_fields_on_templates`, `get_models`, `find_note_ids`, `get_notes_info`, `add_note`, `update_note_fields`), centralizing error message parsing logic currently scattered in `anki_client.py`, and returning raw/lightly-coerced data structures

3. **Create `anki_client/repository.py`** — Implement `AnkiRepository` class consuming `AnkiConnectAPI` with high-level operations: `list_decks() -> list[Deck]`, `list_models() -> list[NoteType]`, `get_model_fields(model_name) -> list[str]`, `list_notes_in_deck(deck) -> list[Note]`, `get_note_detail(note_id) -> Note`, `create_note(...) -> int`, `update_note(...) -> None`, converting API responses into `Deck`, `NoteType`, and `Note` dataclasses

4. **Create `anki_client/cli.py`** — Build CLI using `click` or `typer` (add as dependency in `pyproject.toml`) with subcommands `list-decks`, `list-models`, `show-model-fields --model`, `list-notes --deck [--limit]`, `show-note --id`, `add-note --deck --model --field --tag`, `edit-note --id --field`, all delegating to `AnkiRepository` methods, and replace standalone scripts with console entry point

5. **Update `anki_client/__init__.py`** — Export public API (`AnkiRepository`, `AnkiConnectAPI`, `AnkiConnectTransport`) and maintain backward compatibility by re-exporting `AnkiConnectClient` as deprecated alias for `AnkiRepository`, preserving imports in `conftest.py`, `test_anki_client.py`, `test_anki_integration.py`, and contract tests

6. **Refactor tests for new architecture** — Update `test_anki_client.py` to test `AnkiConnectTransport` (HTTP mocking) and `AnkiConnectAPI` (error parsing) separately, update `test_anki_integration.py` to use `AnkiRepository`, adjust `conftest.py` fixtures to instantiate repository through proper layers, and verify all 24 unit + 17 integration + 8 contract tests still pass

## Further Considerations

1. **CLI framework selection** — Use `click` (simpler, standard) or `typer` (modern, type-based)? Recommend `click` for consistency with Python ecosystem and easier migration from argparse patterns in existing scripts.

2. **Backward compatibility strategy** — Keep deprecated `anki_client.py` as thin wrapper importing from `anki_client/repository.py` temporarily, or immediately break imports and update all references? Recommend immediate migration since this is early-stage project without external consumers.

3. **Configuration injection** — Should `config.py` values be passed as constructor parameters to `AnkiConnectTransport` instead of imported globally? This would improve testability and enable multiple client configurations.
