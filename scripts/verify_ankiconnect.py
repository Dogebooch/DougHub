#!/usr/bin/env python3
"""CLI tool to verify AnkiConnect connectivity and test all required API actions.

This script checks if Anki is running with AnkiConnect installed and tests
all the API actions needed for the DougHub application.

Usage:
    python scripts/verify_ankiconnect.py [--auto-launch]

Options:
    --auto-launch    Attempt to launch Anki if it's not running
"""

import argparse
import sys

from doughub.anki_client import AnkiConnectClient
from doughub.exceptions import AnkiConnectError
from doughub.utils.anki_process import AnkiProcessManager


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"✗ {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"ℹ {message}")


def verify_connection(client: AnkiConnectClient) -> bool:
    """Verify basic connection to AnkiConnect.

    Args:
        client: The AnkiConnect client.

    Returns:
        True if connection is successful, False otherwise.
    """
    print_info("Checking connection to AnkiConnect...")
    try:
        if client.check_connection():
            version = client.get_version()
            print_success(f"Connected to AnkiConnect (API version {version})")
            return True
        else:
            print_error("Unable to connect to AnkiConnect")
            return False
    except AnkiConnectError as e:
        print_error(f"Connection error: {e}")
        return False


def verify_deck_operations(client: AnkiConnectClient) -> bool:
    """Verify deck-related operations.

    Args:
        client: The AnkiConnect client.

    Returns:
        True if all operations succeed, False otherwise.
    """
    print_info("\nTesting deck operations...")
    try:
        # Get deck names
        deck_names = client.get_deck_names()
        print_success(f"Retrieved {len(deck_names)} deck names")
        if deck_names:
            print_info(f"  Example decks: {', '.join(deck_names[:3])}")

        # Get deck names and IDs
        decks_dict = client.get_deck_names_and_ids()
        print_success(f"Retrieved {len(decks_dict)} decks with IDs")

        # Get decks as objects
        decks = client.get_decks()
        print_success(f"Retrieved {len(decks)} Deck objects")

        return True
    except AnkiConnectError as e:
        print_error(f"Deck operations failed: {e}")
        return False


def verify_model_operations(client: AnkiConnectClient) -> bool:
    """Verify note type (model) operations.

    Args:
        client: The AnkiConnect client.

    Returns:
        True if all operations succeed, False otherwise.
    """
    print_info("\nTesting note type operations...")
    try:
        # Get model names
        model_names = client.get_model_names()
        print_success(f"Retrieved {len(model_names)} note type names")
        if model_names:
            print_info(f"  Example note types: {', '.join(model_names[:3])}")

        # Get model names and IDs
        models_dict = client.get_model_names_and_ids()
        print_success(f"Retrieved {len(models_dict)} note types with IDs")

        # Get note types as objects
        note_types = client.get_note_types()
        print_success(f"Retrieved {len(note_types)} NoteType objects")

        # Get field names for Basic note type (should exist in all Anki installations)
        if "Basic" in model_names:
            fields = client.get_model_field_names("Basic")
            print_success(f"Retrieved field names for 'Basic' note type: {fields}")

        return True
    except AnkiConnectError as e:
        print_error(f"Note type operations failed: {e}")
        return False


def verify_note_operations(client: AnkiConnectClient) -> bool:
    """Verify note search and retrieval operations.

    Args:
        client: The AnkiConnect client.

    Returns:
        True if all operations succeed, False otherwise.
    """
    print_info("\nTesting note search operations...")
    try:
        # Search for all notes
        all_note_ids = client.find_notes("")
        print_success(f"Found {len(all_note_ids)} total notes in Anki")

        # If there are notes, get info for the first few
        if all_note_ids:
            sample_ids = all_note_ids[:3]
            notes = client.get_notes_info(sample_ids)
            print_success(f"Retrieved detailed info for {len(notes)} notes")
            if notes:
                print_info(
                    f"  Example note: {notes[0].model_name} - {list(notes[0].fields.keys())}"
                )

        # Test searching by deck
        default_notes = client.find_notes('deck:"Default"')
        print_success(f"Found {len(default_notes)} notes in Default deck")

        return True
    except AnkiConnectError as e:
        print_error(f"Note operations failed: {e}")
        return False


def verify_crud_operations(client: AnkiConnectClient) -> bool:
    """Verify create, update operations for notes.

    Args:
        client: The AnkiConnect client.

    Returns:
        True if all operations succeed, False otherwise.
    """
    print_info("\nTesting note CRUD operations...")
    try:
        # Add a test note
        print_info("  Creating test note...")
        note_id = client.add_note(
            deck_name="Default",
            model_name="Basic",
            fields={
                "Front": "DougHub Verification Test",
                "Back": "This is a test note from verify_ankiconnect.py",
            },
            tags=["doughub-test", "verification"],
        )
        print_success(f"Created test note with ID: {note_id}")

        # Retrieve the note
        print_info("  Retrieving test note...")
        notes = client.get_notes_info([note_id])
        if notes and notes[0].fields["Front"] == "DougHub Verification Test":
            print_success("Retrieved test note successfully")
        else:
            print_error("Failed to retrieve test note with correct data")
            return False

        # Update the note
        print_info("  Updating test note...")
        client.update_note_fields(
            note_id=note_id,
            fields={
                "Front": "DougHub Verification Test (Updated)",
                "Back": "Note was successfully updated",
            },
        )
        print_success("Updated test note successfully")

        # Verify the update
        print_info("  Verifying update...")
        updated_notes = client.get_notes_info([note_id])
        if updated_notes and "Updated" in updated_notes[0].fields["Front"]:
            print_success("Verified update was applied correctly")
        else:
            print_error("Failed to verify note update")
            return False

        print_info(f"\n  Note: Test note (ID {note_id}) was created in Default deck")
        print_info("        You may want to delete it manually from Anki")

        return True
    except AnkiConnectError as e:
        print_error(f"CRUD operations failed: {e}")
        return False


def main() -> int:
    """Main entry point for the verification script.

    Returns:
        Exit code: 0 for success, 1 for failure.
    """
    parser = argparse.ArgumentParser(
        description="Verify AnkiConnect connectivity and API functionality"
    )
    parser.add_argument(
        "--auto-launch",
        action="store_true",
        help="Attempt to launch Anki if it's not running",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("DougHub AnkiConnect Verification Tool")
    print("=" * 60)

    # Attempt to launch Anki if requested
    anki_manager = None
    if args.auto_launch:
        print_info("Auto-launch enabled, checking if Anki is running...")
        anki_manager = AnkiProcessManager()
        if not anki_manager.is_ankiconnect_running():
            print_info("Attempting to launch Anki...")
            if anki_manager.launch_anki(timeout=15.0):
                print_success("Anki launched successfully")
            else:
                print_error("Failed to launch Anki")
                print_info("Please start Anki manually and try again")
                return 1

    # Create client and run tests
    with AnkiConnectClient() as client:
        tests = [
            ("Connection", lambda: verify_connection(client)),
            ("Deck Operations", lambda: verify_deck_operations(client)),
            ("Note Type Operations", lambda: verify_model_operations(client)),
            ("Note Search", lambda: verify_note_operations(client)),
            ("CRUD Operations", lambda: verify_crud_operations(client)),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print_error(f"Unexpected error in {test_name}: {e}")
                results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print_success("\nAll tests passed! AnkiConnect is fully functional.")
        return 0
    else:
        print_error(
            f"\n{total - passed} test(s) failed. Please check the output above."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
