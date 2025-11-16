"""Test launcher script for DougHub UI.

This script launches the PyQt6 application for manual testing.
Requires Anki to be running with AnkiConnect installed.
"""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from doughub.main import main

if __name__ == "__main__":
    sys.exit(main())
