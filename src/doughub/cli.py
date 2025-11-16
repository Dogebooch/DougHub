"""Command-line interface for DougHub.

This module provides CLI commands for running health checks, launching the UI,
and other development/operational tasks.
"""

import os
import subprocess
import sys

import typer

app = typer.Typer(
    name="doughub",
    help="Python-based tooling for Anki deck management",
    add_completion=False,
)


def _print_header(text: str) -> None:
    """Print a styled header."""
    typer.echo(f"\n{'=' * 70}")
    typer.echo(f"  {text}")
    typer.echo(f"{'=' * 70}\n")


def _print_success(text: str) -> None:
    """Print a success message."""
    typer.secho(f"✓ {text}", fg=typer.colors.GREEN)


def _print_error(text: str) -> None:
    """Print an error message."""
    typer.secho(f"✗ {text}", fg=typer.colors.RED)


def _print_info(text: str) -> None:
    """Print an info message."""
    typer.secho(f"ℹ {text}", fg=typer.colors.BLUE)


def _get_stage_description(stage: int) -> str:
    """Get a human-readable description of a validation stage."""
    descriptions = {
        0: "Local invariants (no Anki required)",
        1: "Handshake with live AnkiConnect",
        2: "Core contract checks",
        3: "Negative-path and robustness checks",
    }
    return descriptions.get(stage, "Unknown stage")


def _run_validation_stage(
    stage: int, fail_fast: bool = False, auto_launch: bool = False
) -> bool:
    """Run a specific validation stage.

    Args:
        stage: The stage number (0-3).
        fail_fast: Whether to stop at first test failure.
        auto_launch: Whether to auto-launch Anki if needed.

    Returns:
        True if the stage passed, False otherwise.
    """
    _print_header(f"Stage {stage}: {_get_stage_description(stage)}")

    # Build pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "-m",
        f"contract_stage{stage}",
        f"tests/test_contract_stage{stage}.py",
    ]

    if fail_fast:
        cmd.append("-x")

    if auto_launch:
        # Set environment variable to enable auto-launch
        os.environ["ENABLE_ANKI_AUTO_LAUNCH"] = "true"

    # Run pytest
    _print_info(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        _print_success(f"Stage {stage} passed\n")
        return True
    else:
        _print_error(f"Stage {stage} failed\n")
        return False


@app.command()
def health_check(
    stage: list[int] | None = None,
    fail_fast: bool = False,
    auto_launch: bool = False,
) -> None:
    """Run the AnkiConnect validation pipeline.

    The pipeline consists of 4 stages:
    - Stage 0: Local invariants (no Anki required)
    - Stage 1: Handshake with AnkiConnect
    - Stage 2: Core contract checks
    - Stage 3: Negative-path robustness checks
    """
    # Determine which stages to run
    stages_to_run = stage if stage else [0, 1, 2, 3]

    _print_header("AnkiConnect Validation Pipeline Health Check")
    _print_info(f"Running stages: {', '.join(map(str, stages_to_run))}")

    if fail_fast:
        _print_info("Fail-fast mode enabled")

    if auto_launch:
        _print_info("Auto-launch enabled for Anki")

    # Run each stage
    all_passed = True
    for stage_num in sorted(stages_to_run):
        passed = _run_validation_stage(stage_num, fail_fast, auto_launch)
        if not passed:
            all_passed = False
            if fail_fast:
                _print_error("Stopping due to --fail-fast")
                break

    # Print summary
    _print_header("Summary")
    if all_passed:
        _print_success("All stages passed!")
        raise typer.Exit(0)
    else:
        _print_error("One or more stages failed")
        raise typer.Exit(1)


@app.command()
def launch_ui() -> None:
    """Launch the PyQt6 desktop application.

    Requires Anki to be running with AnkiConnect installed.
    """
    _print_info("Launching DougHub UI...")

    # Import and run the main application
    try:
        from doughub.main import main

        sys.exit(main())
    except ImportError as e:
        _print_error(f"Failed to import UI module: {e}")
        _print_info("Make sure PyQt6 is installed: pip install -e .[dev]")
        raise typer.Exit(2) from e
    except Exception as e:
        _print_error(f"Failed to launch UI: {e}")
        raise typer.Exit(1) from e


# Database inspection commands
db_app = typer.Typer(help="Database inspection and management commands")
app.add_typer(db_app, name="db")


@db_app.command("show-question")
def show_question(question_id: int) -> None:
    """Display detailed information about a specific question.

    Args:
        question_id: The ID of the question to display.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from doughub.config import DATABASE_URL
    from doughub.persistence import QuestionRepository

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    repo = QuestionRepository(session)

    try:
        question = repo.get_question_by_id(question_id)
        if question is None:
            _print_error(f"Question with ID {question_id} not found")
            raise typer.Exit(1)

        _print_header(f"Question {question_id}")

        typer.echo(f"Source:       {question.source.name}")
        typer.echo(f"Source Key:   {question.source_question_key}")
        typer.echo(f"Status:       {question.status}")
        typer.echo(f"Created:      {question.created_at}")
        typer.echo(f"Updated:      {question.updated_at}")

        if question.extraction_path:
            typer.echo(f"Path:         {question.extraction_path}")

        typer.echo(f"\nHTML Preview: {question.raw_html[:200]}...")
        typer.echo(f"\nMetadata:     {question.raw_metadata_json[:200]}...")

        if question.media:
            typer.echo(f"\nMedia Files ({len(question.media)}):")
            for media in question.media:
                typer.echo(
                    f"  - {media.media_role} ({media.mime_type}): {media.relative_path}"
                )
        else:
            typer.echo("\nNo media files")

        typer.echo("")

    finally:
        session.close()
        engine.dispose()


@db_app.command("source-summary")
def source_summary() -> None:
    """Display a summary of all sources and their question counts."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from doughub.config import DATABASE_URL
    from doughub.models import Source

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        stmt = select(Source)
        sources = session.execute(stmt).scalars().all()

        if not sources:
            _print_info("No sources found in the database")
            return

        _print_header("Source Summary")

        typer.echo(f"{'Source Name':<30} {'Questions':<15} {'Description'}")
        typer.echo("-" * 70)

        for source in sources:
            question_count = len(source.questions)
            desc = source.description or "(no description)"
            desc_short = desc[:30] + "..." if len(desc) > 30 else desc
            typer.echo(f"{source.name:<30} {question_count:<15} {desc_short}")

        typer.echo(f"\nTotal sources: {len(sources)}")
        total_questions = sum(len(s.questions) for s in sources)
        typer.echo(f"Total questions: {total_questions}\n")

    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    app()
