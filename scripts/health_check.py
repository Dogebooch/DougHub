#!/usr/bin/env python3
"""Health check script for AnkiConnect validation pipeline.

This script runs the 4-stage validation pipeline:
- Stage 0: Local invariants (no Anki required)
- Stage 1: Handshake with AnkiConnect
- Stage 2: Core contract checks
- Stage 3: Negative-path robustness checks

Usage:
    python scripts/health_check.py              # Run all stages
    python scripts/health_check.py --stage 0    # Run specific stage
    python scripts/health_check.py --stage 1 --stage 2  # Run multiple stages
    python scripts/health_check.py --fail-fast  # Stop at first failure
    python scripts/health_check.py --auto-launch  # Auto-launch Anki if needed

Exit codes:
    0: All requested stages passed
    1: One or more stages failed
    2: Invalid arguments or setup error
"""

import argparse
import subprocess
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"✓ {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"✗ {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"ℹ {text}")


def run_stage(
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
    print_header(f"Stage {stage}: {get_stage_description(stage)}")

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
        import os

        os.environ["ENABLE_ANKI_AUTO_LAUNCH"] = "true"

    # Run pytest
    print_info(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)

    if result.returncode == 0:
        print_success(f"Stage {stage} passed\n")
        return True
    else:
        print_error(f"Stage {stage} failed\n")
        return False


def get_stage_description(stage: int) -> str:
    """Get a human-readable description of a stage."""
    descriptions = {
        0: "Local invariants (no Anki required)",
        1: "Handshake with live AnkiConnect",
        2: "Core contract checks",
        3: "Negative-path and robustness checks",
    }
    return descriptions.get(stage, "Unknown stage")


def main() -> int:
    """Run the health check pipeline."""
    parser = argparse.ArgumentParser(
        description="Run AnkiConnect validation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=[0, 1, 2, 3],
        action="append",
        help="Specific stage(s) to run (can be specified multiple times)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at first test failure within each stage",
    )
    parser.add_argument(
        "--auto-launch",
        action="store_true",
        help="Automatically launch Anki if not running (stages 1-3)",
    )

    args = parser.parse_args()

    # Determine which stages to run
    stages_to_run = args.stage if args.stage else [0, 1, 2, 3]

    print_header("AnkiConnect Validation Pipeline Health Check")
    print_info(f"Running stages: {', '.join(map(str, stages_to_run))}")

    if args.fail_fast:
        print_info("Fail-fast mode enabled")

    if args.auto_launch:
        print_info("Auto-launch enabled for Anki")

    # Run each stage
    all_passed = True
    for stage in sorted(stages_to_run):
        passed = run_stage(stage, args.fail_fast, args.auto_launch)
        if not passed:
            all_passed = False
            if args.fail_fast:
                print_error("Stopping due to --fail-fast")
                break

    # Print summary
    print_header("Summary")
    if all_passed:
        print_success("All stages passed!")
        return 0
    else:
        print_error("One or more stages failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
