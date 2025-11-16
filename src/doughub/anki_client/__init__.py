"""AnkiConnect client package with layered architecture."""

from .api import AnkiConnectAPI
from .repository import AnkiRepository
from .transport import AnkiConnectTransport

# Backward compatibility alias
AnkiConnectClient = AnkiRepository

__all__ = [
    "AnkiConnectTransport",
    "AnkiConnectAPI",
    "AnkiRepository",
    "AnkiConnectClient",  # Deprecated, use AnkiRepository
]
