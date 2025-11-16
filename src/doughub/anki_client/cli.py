"""Command-line interface for DougHub Anki operations.

Provides CLI commands for interacting with Anki through AnkiConnect,
allowing users to list decks, models, notes, and perform CRUD operations
from the terminal.
"""

import sys
from typing import Any

import click

from ..anki_process import AnkiProcessManager
from .repository import AnkiRepository


@click.group()
@click.pass_context
def cli(ctx: Any) -> None:
    """DougHub - Anki deck management CLI.

    Interact with Anki through AnkiConnect from the command line.
    """
    # Store repository in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["repository"] = AnkiRepository()


@cli.command("list-decks")
@click.pass_context
def list_decks(ctx: Any) -> None:
    """List all available decks."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        decks = repo.list_decks()
        if not decks:
            click.echo("No decks found.")
            return

        click.echo("Available decks:")
        for deck in sorted(decks, key=lambda d: d.name):
            click.echo(f"  {deck.name} (ID: {deck.id})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("list-models")
@click.pass_context
def list_models(ctx: Any) -> None:
    """List all available note types (models)."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        models = repo.list_models()
        if not models:
            click.echo("No note types found.")
            return

        click.echo("Available note types:")
        for model in sorted(models, key=lambda m: m.name):
            field_count = len(model.fields) if model.fields else 0
            click.echo(f"  {model.name} (ID: {model.id}, {field_count} fields)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("show-model-fields")
@click.option("--model", required=True, help="Note type name")
@click.pass_context
def show_model_fields(ctx: Any, model: str) -> None:
    """Show field names for a note type."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        fields = repo.get_model_fields(model)
        if not fields:
            click.echo(f"Note type '{model}' has no fields.")
            return

        click.echo(f"Fields for '{model}':")
        for i, field in enumerate(fields, 1):
            click.echo(f"  {i}. {field}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("list-notes")
@click.option("--deck", required=True, help="Deck name to list notes from")
@click.option("--limit", type=int, default=None, help="Maximum number of notes to show")
@click.pass_context
def list_notes(ctx: Any, deck: str, limit: int | None) -> None:
    """List notes in a deck."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        notes = repo.list_notes_in_deck(deck, limit=limit)
        if not notes:
            click.echo(f"No notes found in deck '{deck}'.")
            return

        click.echo(f"Notes in '{deck}' ({len(notes)} found):")
        click.echo(f"{'ID':<10} {'Model':<20} {'First Field'}")
        click.echo("-" * 70)

        for note in notes:
            # Get first field value as preview
            first_field = ""
            if note.fields:
                first_field = next(iter(note.fields.values()), "")
                # Truncate long values
                if len(first_field) > 40:
                    first_field = first_field[:37] + "..."

            click.echo(f"{note.note_id:<10} {note.model_name:<20} {first_field}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("show-note")
@click.option("--id", "note_id", type=int, required=True, help="Note ID to display")
@click.pass_context
def show_note(ctx: Any, note_id: int) -> None:
    """Show detailed information about a note."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        note = repo.get_note_detail(note_id)

        click.echo(f"Note ID: {note.note_id}")
        click.echo(f"Model: {note.model_name}")
        click.echo(f"Tags: {', '.join(note.tags) if note.tags else '(none)'}")
        click.echo(
            f"Cards: {', '.join(map(str, note.cards)) if note.cards else '(none)'}"
        )
        click.echo("\nFields:")

        for field_name, field_value in note.fields.items():
            # Handle multiline values
            lines = field_value.split("\n")
            click.echo(f"  {field_name}:")
            for line in lines:
                click.echo(f"    {line}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("add-note")
@click.option("--deck", required=True, help="Deck name to add note to")
@click.option("--model", required=True, help="Note type name")
@click.option(
    "--field",
    "fields",
    multiple=True,
    required=True,
    help='Field value in format "FieldName=value" (can be specified multiple times)',
)
@click.option(
    "--tag", "tags", multiple=True, help="Tag to add (can be specified multiple times)"
)
@click.pass_context
def add_note(
    ctx: Any, deck: str, model: str, fields: tuple[str, ...], tags: tuple[str, ...]
) -> None:
    """Add a new note to Anki."""
    repo: AnkiRepository = ctx.obj["repository"]

    # Parse field arguments
    field_dict: dict[str, str] = {}
    for field_arg in fields:
        if "=" not in field_arg:
            click.echo(
                f"Error: Invalid field format '{field_arg}'. Expected 'FieldName=value'",
                err=True,
            )
            sys.exit(1)

        field_name, field_value = field_arg.split("=", 1)
        field_dict[field_name.strip()] = field_value.strip()

    tag_list = list(tags) if tags else None

    try:
        note_id = repo.create_note(deck, model, field_dict, tag_list)
        click.echo(f"Successfully created note with ID: {note_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("edit-note")
@click.option("--id", "note_id", type=int, required=True, help="Note ID to edit")
@click.option(
    "--field",
    "fields",
    multiple=True,
    required=True,
    help='Field value in format "FieldName=value" (can be specified multiple times)',
)
@click.pass_context
def edit_note(ctx: Any, note_id: int, fields: tuple[str, ...]) -> None:
    """Edit an existing note's fields."""
    repo: AnkiRepository = ctx.obj["repository"]

    # Parse field arguments
    field_dict: dict[str, str] = {}
    for field_arg in fields:
        if "=" not in field_arg:
            click.echo(
                f"Error: Invalid field format '{field_arg}'. Expected 'FieldName=value'",
                err=True,
            )
            sys.exit(1)

        field_name, field_value = field_arg.split("=", 1)
        field_dict[field_name.strip()] = field_value.strip()

    try:
        repo.update_note(note_id, field_dict)
        click.echo(f"Successfully updated note {note_id}")

        # Show updated note
        click.echo("\nUpdated note:")
        ctx.invoke(show_note, note_id=note_id)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("check-connection")
@click.pass_context
def check_connection(ctx: Any) -> None:
    """Check if AnkiConnect is accessible."""
    repo: AnkiRepository = ctx.obj["repository"]

    try:
        if repo.check_connection():
            version = repo.get_version()
            click.echo(f"✓ AnkiConnect is accessible (version {version})")
        else:
            click.echo("✗ AnkiConnect is not accessible", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error checking connection: {e}", err=True)
        sys.exit(1)


@cli.command("launch-anki")
@click.option("--timeout", type=float, default=15.0, help="Timeout in seconds")
def launch_anki(timeout: float) -> None:
    """Launch Anki with AnkiConnect support."""
    manager = AnkiProcessManager()

    if manager.is_ankiconnect_running():
        click.echo("Anki is already running.")
        return

    click.echo(f"Launching Anki (timeout: {timeout}s)...")
    success = manager.launch_anki(timeout=timeout)

    if success:
        click.echo("✓ Anki launched successfully and AnkiConnect is accessible")
    else:
        click.echo("✗ Failed to launch Anki or AnkiConnect is not accessible", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
