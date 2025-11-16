"""Configuration for DougHub application."""

import os

# AnkiConnect settings
ANKICONNECT_URL: str = os.getenv("ANKICONNECT_URL", "http://127.0.0.1:8765")
ANKICONNECT_VERSION: int = int(os.getenv("ANKICONNECT_VERSION", "6"))
ANKICONNECT_TIMEOUT: float = float(os.getenv("ANKICONNECT_TIMEOUT", "10.0"))

# Anki application settings
ANKI_EXECUTABLE: str = os.getenv("ANKI_EXECUTABLE", "anki")
ANKI_TEST_PROFILE: str = os.getenv("ANKI_TEST_PROFILE", "DougHub_Testing_Suite")

# Testing configuration
ENABLE_ANKI_AUTO_LAUNCH: bool = os.getenv(
    "ENABLE_ANKI_AUTO_LAUNCH", "true"
).lower() in (
    "true",
    "1",
    "yes",
)
