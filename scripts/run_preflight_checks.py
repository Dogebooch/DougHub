#!/usr/bin/env python
"""Standalone script to run preflight validation checks.

This script is intended for use in CI/CD pipelines and testing environments
to validate the application environment before deployment or testing.

Exit codes:
    0: All checks passed
    1: Fatal errors detected
    2: Warnings detected (non-fatal, but worth investigating)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from doughub.preflight import run_preflight_checks


def main() -> int:
    """Run preflight checks and report results."""
    print("=" * 70)
    print("DougHub Preflight Validation Checks")
    print("=" * 70)
    print()

    report = run_preflight_checks()

    print()
    print("=" * 70)
    print(f"Results: {len(report.checks)} checks performed")
    print("=" * 70)
    print()

    # Display all checks with status
    for check in report.checks:
        if check.severity.value == "INFO":
            symbol = "✓"
        elif check.severity.value == "WARN":
            symbol = "⚠"
        else:  # FATAL
            symbol = "❌"

        print(f"{symbol} [{check.severity.value:5s}] {check.name:30s}")
        print(f"         {check.message}")
        print()

    print("=" * 70)

    # Determine exit code and final status
    if report.has_fatal:
        print("❌ FATAL: Environment validation failed")
        print(f"   {len(report.fatal_messages)} fatal error(s) detected")
        print()
        print("Fatal errors must be fixed before the application can run:")
        for i, msg in enumerate(report.fatal_messages, 1):
            print(f"  {i}. {msg}")
        print()
        return 1
    elif report.warnings:
        print("⚠  WARNING: Environment has non-critical issues")
        print(f"   {len(report.warnings)} warning(s) detected")
        print()
        print("Application can run, but some features may be unavailable:")
        for i, msg in enumerate(report.warnings, 1):
            print(f"  {i}. {msg}")
        print()
        return 2
    else:
        print("✓  SUCCESS: All validation checks passed")
        print("   Environment is healthy and ready")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
