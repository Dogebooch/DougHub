#!/usr/bin/env python3
"""
Local server to receive extracted page data from Tampermonkey script.
Displays the received data in the terminal for debugging.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store extractions for review
extractions = []

# Create output directory for saved extractions
OUTPUT_DIR = Path(__file__).parent.parent / "extractions"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.route('/extract', methods=['POST', 'OPTIONS'])
def receive_extraction():
    """Receive and display extracted page data from Tampermonkey script."""

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Store the extraction
        extractions.append(data)
        extraction_index = len(extractions) - 1

        # Generate filename based on timestamp and site
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_name = data.get('siteName', 'unknown').replace(' ', '_')
        base_filename = f"{timestamp}_{site_name}_{extraction_index}"

        # Save HTML to file
        html_file = OUTPUT_DIR / f"{base_filename}.html"
        html_file.write_text(data.get('pageHTML', ''), encoding='utf-8')

        # Save JSON metadata (without the full HTML to keep it readable)
        json_data = {
            'timestamp': data.get('timestamp'),
            'url': data.get('url'),
            'hostname': data.get('hostname'),
            'siteName': data.get('siteName'),
            'elementCount': data.get('elementCount'),
            'bodyText': data.get('bodyText'),
            'elements': data.get('elements', [])
        }
        json_file = OUTPUT_DIR / f"{base_filename}.json"
        json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')

        # Print to terminal with formatting
        print("\n" + "=" * 80)
        print(f"📥 NEW EXTRACTION RECEIVED at {data.get('timestamp', 'unknown')}")
        print("=" * 80)
        print(f"🌐 URL: {data.get('url', 'unknown')}")
        print(f"🏥 Site: {data.get('siteName', 'unknown')}")
        print(f"📊 Elements found: {data.get('elementCount', 0)}")
        print(f"📏 HTML size: {len(data.get('pageHTML', '')) / 1024:.1f} KB")
        print("=" * 80)

        # Print file locations
        print(f"\n💾 Files saved:")
        print(f"   HTML: {html_file}")
        print(f"   JSON: {json_file}")

        # Print body text preview
        body_text = data.get('bodyText', '')
        if body_text:
            preview = body_text[:500].replace('\n', ' ')
            print(f"\n📄 Body Text Preview:\n{preview}...")

        # Print some interesting elements
        elements = data.get('elements', [])
        if elements:
            print("\n🔍 Sample Elements (first 10):")
            for i, elem in enumerate(elements[:10]):
                if elem.get('text'):
                    print(f"  {i+1}. [{elem['tag']}] {elem['selector']}: {elem['text'][:60]}...")

        print("\n" + "=" * 80)
        print(f"✅ Total extractions received: {len(extractions)}")
        print(f"📂 View HTML: {html_file.absolute()}")
        print("=" * 80 + "\n")

        return jsonify({
            "status": "success",
            "message": "Data received successfully",
            "extraction_count": len(extractions),
            "files": {
                "html": str(html_file),
                "json": str(json_file)
            }
        }), 200

    except Exception as e:
        print(f"\n❌ ERROR receiving extraction: {e}\n", file=sys.stderr)
        return jsonify({"error": str(e)}), 500


@app.route('/extractions', methods=['GET'])
def list_extractions():
    """List all received extractions."""
    return jsonify({
        "total": len(extractions),
        "extractions": [
            {
                "timestamp": ext.get('timestamp'),
                "url": ext.get('url'),
                "siteName": ext.get('siteName'),
                "elementCount": ext.get('elementCount')
            }
            for ext in extractions
        ]
    }), 200


@app.route('/extractions/<int:index>', methods=['GET'])
def get_extraction(index):
    """Get a specific extraction by index."""
    if 0 <= index < len(extractions):
        return jsonify(extractions[index]), 200
    return jsonify({"error": "Extraction not found"}), 404


@app.route('/clear', methods=['POST'])
def clear_extractions():
    """Clear all stored extractions."""
    extractions.clear()
    print("\n🗑️  All extractions cleared\n")
    return jsonify({"status": "success", "message": "All extractions cleared"}), 200


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "message": "Tampermonkey Extraction Server",
        "extractions_count": len(extractions),
        "endpoints": {
            "POST /extract": "Receive extraction from Tampermonkey",
            "GET /extractions": "List all extractions",
            "GET /extractions/<index>": "Get specific extraction",
            "POST /clear": "Clear all extractions"
        }
    }), 200


def main():
    """Run the Flask server."""
    print("\n" + "=" * 80)
    print("🚀 TAMPERMONKEY EXTRACTION SERVER")
    print("=" * 80)
    print("Server is running on http://localhost:5000")
    print("Waiting for extractions from Tampermonkey script...")
    print("=" * 80 + "\n")
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user\n")
    except Exception as e:
        print(f"\n❌ Server error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
