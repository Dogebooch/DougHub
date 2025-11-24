# Test Fixtures

This directory contains fixtures for testing the extraction system. All fixtures are based on real extraction data from past successful extractions.

## HTML Fixtures

### `html/sample_mksap.html`
Based on real MKSAP 19 extraction from `extractions/20251116_150929_MKSAP_19_0.html`.

**Question Content:**
- Topic: Infectious Disease - Travelers' Diarrhea
- Clinical vignette: 62-year-old woman with 4-day history of diarrhea after trip to Guatemala
- Format: Multiple choice with 4 answer options (A-D)
- Includes: Clinical presentation, physical exam findings, answer choices with peer statistics
- Structure: Complete HTML document with realistic MKSAP page structure

**Test Usage:**
- HTML fixture immutability tests
- Input validation tests
- Extraction pipeline regression tests

### `html/sample_acep.html`
Based on real ACEP PeerPrep extraction from `extractions/20251116_145626_ACEP_PeerPrep_2.html`.

**Question Content:**
- Topic: Emergency Medicine - Bilateral Uveitis/Sarcoidosis
- Clinical vignette: 37-year-old woman with bilateral uveitis and chest x-ray showing hilar adenopathy
- Format: Multiple choice with 4 answer options with peer comparison percentages
- Includes: Question stem, image reference, answer feedback with reasoning and distractor analysis
- Structure: Angular-based web application structure

**Test Usage:**
- Cross-platform format validation
- Different HTML structure handling
- Image reference extraction tests

### `html/malformed/`
Contains intentionally malformed HTML files for edge case testing:
- `unclosed_tags.html` - HTML with unclosed tags
- `invalid_chars.html` - HTML with invalid characters
- `empty_tags.html` - HTML with empty tags

**Test Usage:**
- Input validation edge cases
- Error handling verification
- Graceful degradation tests

## Golden Set Fixtures

### `golden_set/sample_001.json`
MKSAP 19 travelers' diarrhea question with expected extraction outputs.

**Structure:**
```json
{
  "description": "Human-readable description",
  "source": "Reference to original extraction file",
  "raw_html": "Complete HTML fixture content",
  "expected_context_html": "Expected clinical vignette extraction",
  "expected_stem_html": "Expected question stem extraction"
}
```

**Expected Outputs:**
- Context: Patient presentation and physical exam findings
- Stem: "Which of the following is the most appropriate treatment?"

### `golden_set/sample_002.json`
ACEP PeerPrep bilateral uveitis question with expected extraction outputs.

**Expected Outputs:**
- Context: Patient presentation with bilateral uveitis and chest x-ray findings
- Stem: "What is the next best step?"

## Maintenance

When updating fixtures:
1. Base new fixtures on real extraction data from `extractions/` directory
2. Simplify HTML structure while preserving key elements needed for testing
3. Update golden set expected outputs to match extraction goals
4. Update hash values in tests if fixture content changes
5. Document the source extraction file and question content

## Test Coverage

These fixtures support validation stages A-F:
- **Stage A**: HTML fixture regression tests (immutability, hashing)
- **Stage B**: Input contract validation (edge cases, malformed input)
- **Stage C**: JSON schema validation (DTO structure)
- **Stage D**: Content-level validation (golden set comparison, leakage detection)
- **Stage E**: Persistence layer validation (storage, retrieval)
- **Stage F**: UI rendering validation (component display)
