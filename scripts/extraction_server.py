#!/usr/bin/env python3
"""
Local server to receive extracted page data from Tampermonkey script.
Displays the received data in the terminal for debugging.

Now includes automatic persistence to the SQLite database.
"""

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.config import DATABASE_URL, MEDIA_ROOT
from doughub.models import Base
from doughub.persistence import QuestionRepository

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store extractions for review
extractions = []

# Create output directory for saved extractions
OUTPUT_DIR = Path(__file__).parent.parent / "extractions"
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize database connection
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Ensure media root exists
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)


def parse_source_and_key(data: dict, base_filename: str) -> tuple[str, str]:
    """Extract source name and question key from extraction data.

    Args:
        data: Extraction data dictionary
        base_filename: Generated base filename

    Returns:
        Tuple of (source_name, question_key)
    """
    # Get site name from the extraction data
    site_name = data.get("siteName", "unknown").replace(" ", "_")

    # Extract question key from the URL or use the extraction index
    url = data.get("url", "")

    # For MKSAP and ACEP URLs, extract the question ID from the URL
    # Examples:
    #   https://mksap19.acponline.org/app/question-bank/random-question/xvUuU0LgBl5Re8Wi/4
    #   https://mksap19.acponline.org/app/question-bank/x3/x3_id/mk19x_3_id_q008
    #   https://learn.acep.org/...
    parts = url.rstrip("/").split("/")
    if parts and len(parts) > 0:
        # Always use the last part of the URL as the question key
        question_key = parts[-1]
        # If it's empty or looks like a session ID (very long alphanumeric), try the second-to-last part
        if not question_key or len(question_key) > 50:
            question_key = parts[-2] if len(parts) > 1 else base_filename.split("_")[-1]
    else:
        # Fallback: use the extraction index from base_filename
        question_key = base_filename.split("_")[-1]

    return site_name, question_key


def copy_image_to_media_root(source_path: Path, source_name: str, question_key: str, img_index: int) -> str:
    """Copy an image file to the media storage directory.

    Args:
        source_path: Path to the source image file in extractions/
        source_name: Name of the source
        question_key: Question key
        img_index: Index of the image

    Returns:
        Relative path to the copied file
    """
    source_path = Path(source_path)
    media_root = Path(MEDIA_ROOT)

    # Create source-specific directory
    source_dir = media_root / source_name
    source_dir.mkdir(parents=True, exist_ok=True)

    # Create destination filename
    ext = source_path.suffix
    dest_filename = f"{question_key}_img{img_index}{ext}"
    dest_path = source_dir / dest_filename

    # Copy file if source exists
    if source_path.exists():
        import shutil

        shutil.copy2(source_path, dest_path)
        print(f"   [DB] Copied to media_root: {source_name}/{dest_filename}")

    # Return relative path
    return f"{source_name}/{dest_filename}"


def persist_to_database(data: dict, html_file: Path, json_file: Path, downloaded_images: list, base_filename: str) -> tuple[bool, str | None]:
    """Persist the extraction to the database.

    Args:
        data: Extraction data dictionary
        html_file: Path to saved HTML file
        json_file: Path to saved JSON file
        downloaded_images: List of downloaded image metadata
        base_filename: Base filename for the extraction

    Returns:
        Tuple of (success: bool, error_message: str or None)
    """
    session = None
    try:
        session = SessionLocal()
        repo = QuestionRepository(session)

        # Parse source name and question key
        source_name, question_key = parse_source_and_key(data, base_filename)

        print(f"[DB] Persisting: {source_name}/{question_key}")

        # Get or create source
        source = repo.get_or_create_source(name=source_name)
        source_id: int = source.source_id  # type: ignore

        # Check if question already exists
        existing_question = repo.get_question_by_source_key(source_id, question_key)
        if existing_question:
            print(
                f"[DB] Question already exists in database: {source_name}/{question_key}"
            )
            repo.commit()
            return True, None

        # Read HTML content
        html_content = html_file.read_text(encoding="utf-8")

        # Prepare metadata JSON (the data we already saved)
        with open(json_file, encoding="utf-8") as f:
            metadata = json.load(f)

        # Create question data
        question_data = {
            "source_id": source_id,
            "source_question_key": question_key,
            "raw_html": html_content,
            "raw_metadata_json": json.dumps(metadata),
            "status": "extracted",
            "extraction_path": str(json_file.parent / json_file.stem),
        }

        # Add question to database
        question = repo.add_question(question_data)
        question_id: int = question.question_id  # type: ignore
        print(f"[DB] Added question to database (ID: {question_id})")

        # Process and persist media files
        for img_info in downloaded_images:
            if "local_path" not in img_info:
                continue

            local_path = Path(img_info["local_path"])
            if not local_path.exists():
                print(f"[DB] Warning: Image file not found: {local_path}")
                continue

            # Copy image to media_root
            relative_path = copy_image_to_media_root(
                local_path, source_name, question_key, img_info["index"]
            )

            # Determine MIME type from extension
            ext = local_path.suffix.lower()
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            mime_type = mime_types.get(ext, "application/octet-stream")

            # Add media record
            media_data = {
                "media_role": "image",
                "media_type": "question_image",
                "mime_type": mime_type,
                "relative_path": relative_path,
            }
            media = repo.add_media_to_question(question_id, media_data)
            media_id: int = media.media_id  # type: ignore
            print(f"[DB]   Added media (ID: {media_id}): {relative_path}")

        # Commit the transaction
        repo.commit()
        print("[DB] ✓ Successfully persisted to database")
        return True, None

    except Exception as e:
        if session:
            session.rollback()
        error_msg = f"Database persistence failed: {e}"
        print(f"[DB] ✗ {error_msg}", file=sys.stderr)
        return False, error_msg
    finally:
        if session:
            session.close()


def download_images(images, base_filename):
    """Download images from URLs and save locally.

    Args:
        images: List of image dictionaries with 'url', 'title', etc.
        base_filename: Base filename for saving (without extension)

    Returns:
        List of dictionaries with local paths and metadata
    """
    downloaded = []

    for idx, img in enumerate(images):
        try:
            url = img.get("url")
            if not url:
                continue

            # Parse URL to get file extension
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            ext = Path(path).suffix or ".jpg"  # Default to .jpg if no extension

            # Generate filename: base_filename_img0.jpg, base_filename_img1.jpg, etc.
            img_filename = f"{base_filename}_img{idx}{ext}"
            img_path = OUTPUT_DIR / img_filename

            # Download the image
            print(f"   Downloading image {idx + 1}/{len(images)}: {url}")
            urllib.request.urlretrieve(url, img_path)

            downloaded.append(
                {
                    "index": idx,
                    "url": url,
                    "local_path": str(img_path),
                    "filename": img_filename,
                    "title": img.get("title", ""),
                    "type": img.get("type", "image"),
                }
            )

            print(f"   [OK] Saved: {img_filename}")

        except Exception as e:
            print(f"   [FAIL] Failed to download image {idx}: {e}")
            downloaded.append(
                {"index": idx, "url": img.get("url", ""), "error": str(e)}
            )

    return downloaded


@app.route("/extract", methods=["POST", "OPTIONS"])
def receive_extraction():
    """Receive and display extracted page data from Tampermonkey script."""

    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Store the extraction
        extractions.append(data)
        extraction_index = len(extractions) - 1

        # Generate filename based on timestamp and site
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_name = data.get("siteName", "unknown").replace(" ", "_")
        base_filename = f"{timestamp}_{site_name}_{extraction_index}"

        # Save HTML to file
        html_file = OUTPUT_DIR / f"{base_filename}.html"
        html_file.write_text(data.get("pageHTML", ""), encoding="utf-8")

        # Download images if present
        downloaded_images = []
        images = data.get("images", [])
        if images:
            print(f"\n[DOWNLOAD] Downloading {len(images)} image(s)...")
            downloaded_images = download_images(images, base_filename)

        # Save JSON metadata (without the full HTML to keep it readable)
        json_data = {
            "timestamp": data.get("timestamp"),
            "url": data.get("url"),
            "hostname": data.get("hostname"),
            "siteName": data.get("siteName"),
            "elementCount": data.get("elementCount"),
            "imageCount": data.get("imageCount", 0),
            "bodyText": data.get("bodyText"),
            "elements": data.get("elements", []),
            "images": downloaded_images,
        }
        json_file = OUTPUT_DIR / f"{base_filename}.json"
        json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

        # Print to terminal with formatting
        print("\n" + "=" * 80)
        print(f"[NEW] EXTRACTION RECEIVED at {data.get('timestamp', 'unknown')}")
        print("=" * 80)
        print(f"[URL] {data.get('url', 'unknown')}")
        print(f"[SITE] {data.get('siteName', 'unknown')}")
        print(f"[ELEMENTS] {data.get('elementCount', 0)}")
        print(f"[IMAGES] {data.get('imageCount', 0)}")
        print(f"[SIZE] {len(data.get('pageHTML', '')) / 1024:.1f} KB")
        print("=" * 80)

        # Print file locations
        print("\n[SAVED] Files saved:")
        print(f"   HTML: {html_file}")
        print(f"   JSON: {json_file}")

        # Persist to database
        db_success, db_error = persist_to_database(
            data, html_file, json_file, downloaded_images, base_filename
        )

        # Print body text preview
        body_text = data.get("bodyText", "")
        if body_text:
            preview = body_text[:500].replace("\n", " ")
            print(f"\n[PREVIEW] Body Text Preview:\n{preview}...")

        # Print some interesting elements
        elements = data.get("elements", [])
        if elements:
            print("\n[SAMPLE] Sample Elements (first 10):")
            for i, elem in enumerate(elements[:10]):
                if elem.get("text"):
                    print(
                        f"  {i + 1}. [{elem['tag']}] {elem['selector']}: {elem['text'][:60]}..."
                    )

        print("\n" + "=" * 80)
        print(f"[OK] Total extractions received: {len(extractions)}")
        print(f"[FILE] View HTML: {html_file.absolute()}")
        if db_success:
            print("[DB] ✓ Persisted to database")
        else:
            print(f"[DB] ✗ Database error: {db_error}")
        print("=" * 80 + "\n")

        response_data = {
            "status": "success",
            "message": "Data received successfully",
            "extraction_count": len(extractions),
            "files": {
                "html": str(html_file),
                "json": str(json_file),
                "images": [
                    img.get("local_path")
                    for img in downloaded_images
                    if "local_path" in img
                ],
            },
            "database": {
                "persisted": db_success,
                "error": db_error if not db_success else None,
            },
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"\n[ERROR] ERROR receiving extraction: {e}\n", file=sys.stderr)
        return jsonify({"error": str(e)}), 500


@app.route("/extractions", methods=["GET"])
def list_extractions():
    """List all received extractions."""
    return jsonify(
        {
            "total": len(extractions),
            "extractions": [
                {
                    "timestamp": ext.get("timestamp"),
                    "url": ext.get("url"),
                    "siteName": ext.get("siteName"),
                    "elementCount": ext.get("elementCount"),
                }
                for ext in extractions
            ],
        }
    ), 200


@app.route("/extractions/<int:index>", methods=["GET"])
def get_extraction(index):
    """Get a specific extraction by index."""
    if 0 <= index < len(extractions):
        return jsonify(extractions[index]), 200
    return jsonify({"error": "Extraction not found"}), 404


@app.route("/clear", methods=["POST"])
def clear_extractions():
    """Clear all stored extractions."""
    extractions.clear()
    print("\n[CLEAR] All extractions cleared\n")
    return jsonify({"status": "success", "message": "All extractions cleared"}), 200


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "running",
            "message": "Tampermonkey Extraction Server",
            "extractions_count": len(extractions),
            "endpoints": {
                "POST /extract": "Receive extraction from Tampermonkey",
                "GET /extractions": "List all extractions",
                "GET /extractions/<index>": "Get specific extraction",
                "POST /clear": "Clear all extractions",
            },
        }
    ), 200


def main():
    """Run the Flask server."""
    print("\n" + "=" * 80)
    print("[SERVER] TAMPERMONKEY EXTRACTION SERVER")
    print("=" * 80)
    print("Server is running on http://localhost:5000")
    print("Waiting for extractions from Tampermonkey script...")
    print("=" * 80 + "\n")

    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n[STOP] Server stopped by user\n")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
