# Extraction Output Directory

This directory contains HTML and JSON files extracted from medical question websites (ACEP PeerPrep, MKSAP) via the Tampermonkey userscript.

## File Naming Convention

Files are named: `YYYYMMDD_HHMMSS_SiteName_Index.{html,json}`

Example:
- `20251116_143052_ACEP_PeerPrep_0.html` - Full HTML of the page
- `20251116_143052_ACEP_PeerPrep_0.json` - Metadata and extracted elements

## Contents

### HTML Files
- Complete HTML source of the extracted page
- Open in any browser to view the original page structure
- Use browser DevTools to inspect and find CSS selectors

### JSON Files
- Metadata about the extraction (timestamp, URL, site name)
- Body text of the page
- Array of all extracted elements with:
  - Tag name
  - ID (if present)
  - Classes (if present)
  - Suggested CSS selector
  - Text content preview

## Usage

1. **View HTML**: Open `.html` files in a browser to see the page structure
2. **Inspect Elements**: Right-click → Inspect to find CSS selectors
3. **Review JSON**: Open `.json` files to see the structured element data
4. **Find Selectors**: Use the element table to identify question, answer, and explanation selectors

## Cleanup

These files are for debugging only. Delete old extractions periodically to save disk space.
