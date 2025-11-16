#!/usr/bin/env python3
"""Test script to verify extraction server integration with database."""

import json
from pathlib import Path

# Sample extraction data matching what Tampermonkey sends
test_extraction = {
    "timestamp": "2025-11-16T20:00:00.000Z",
    "url": "https://mksap19.acponline.org/app/question-bank/test/test_id/mk19x_test_q999",
    "hostname": "mksap19.acponline.org",
    "siteName": "MKSAP 19",
    "elementCount": 500,
    "imageCount": 0,
    "bodyText": "This is a test question for database integration...",
    "pageHTML": "<html><body><h1>Test Question</h1><p>This is test content</p></body></html>",
    "elements": [
        {"tag": "h1", "text": "Test Question", "selector": "h1"},
        {"tag": "p", "text": "This is test content", "selector": "p"},
    ],
    "images": [],
}


def test_server_integration():
    """Send test extraction to server and verify database persistence."""
    import requests

    server_url = "http://localhost:5000/extract"

    print("=" * 80)
    print("Testing Extraction Server Database Integration")
    print("=" * 80)
    print("\nSending test extraction to server...")

    try:
        response = requests.post(
            server_url,
            json=test_extraction,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✓ Server Response:")
            print(json.dumps(result, indent=2))

            # Check database status
            db_status = result.get("database", {})
            if db_status.get("persisted"):
                print("\n✓ SUCCESS: Data persisted to database!")
            else:
                print(f"\n✗ ERROR: Database persistence failed: {db_status.get('error')}")

            # Verify files were created
            files = result.get("files", {})
            if files.get("html"):
                html_path = Path(files["html"])
                if html_path.exists():
                    print(f"✓ HTML file created: {html_path}")
                else:
                    print(f"✗ HTML file not found: {html_path}")

            if files.get("json"):
                json_path = Path(files["json"])
                if json_path.exists():
                    print(f"✓ JSON file created: {json_path}")
                else:
                    print(f"✗ JSON file not found: {json_path}")

        else:
            print(f"\n✗ Server returned error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to server")
        print("Make sure the extraction server is running:")
        print("  python scripts/extraction_server.py")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

    print("\n" + "=" * 80)
    return True


if __name__ == "__main__":
    import sys

    success = test_server_integration()
    sys.exit(0 if success else 1)
