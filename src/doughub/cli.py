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


if __name__ == "__main__":
    app()
