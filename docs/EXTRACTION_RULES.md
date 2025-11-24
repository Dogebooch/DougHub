# Extraction Rules: Context vs. Stem Splitting

## Overview

This document defines the official rules for splitting raw HTML question content into two distinct fields: `question_context_html` and `question_stem_html`. These rules serve as the single source of truth for the LLM-based extraction pipeline and for developers implementing or validating the extraction behavior.

## Field Definitions

### `question_context_html`

The **context** contains background information, case scenarios, vignettes, or any setup information that provides necessary background for understanding the question but does not ask the question itself.

**Characteristics:**
- May be empty (default: `""`) for questions without contextual setup
- Contains patient presentations, clinical scenarios, case vignettes, or background narratives
- Does NOT contain the actual question being asked
- Does NOT contain answer options (A, B, C, D, etc.)
- Does NOT contain explanations, rationales, or educational content

**Examples of context content:**
- Patient demographics and history: "A 45-year-old woman presents to the emergency department..."
- Laboratory results and vital signs
- Timeline of events leading to the clinical situation
- Background information about a case or scenario
- Relevant medical history or physical examination findings

### `question_stem_html`

The **stem** contains the actual question being asked. This is the interrogative portion that the test-taker must answer.

**Characteristics:**
- REQUIRED field (must not be empty)
- Contains the specific question or instruction
- Often ends with a question mark (`?`)
- Often begins with common interrogative phrases
- Does NOT contain answer options (A, B, C, D, etc.)
- Does NOT contain explanations, rationales, or educational content

**Examples of question stems:**
- "Which of the following is the most appropriate next step in management?"
- "What is the most likely diagnosis?"
- "Which laboratory finding would you expect?"
- "What should be done first?"
- "Select the best answer."

## Splitting Rules

### Rule 1: Context Separation
If the HTML contains a clear narrative or case presentation followed by a question, split them:
- Everything up to (but not including) the interrogative portion → `question_context_html`
- The interrogative portion itself → `question_stem_html`

### Rule 2: Context-Free Questions
If the HTML contains only a direct question without any setup or vignette:
- `question_context_html` = `""` (empty string)
- `question_stem_html` = the entire question

### Rule 3: Multiple Paragraphs
If the context contains multiple paragraphs or sections:
- Include ALL contextual paragraphs in `question_context_html`
- Only the final interrogative statement goes in `question_stem_html`

### Rule 4: HTML Structure Preservation
- Preserve the HTML structure (tags, formatting) within each field
- Do not strip HTML tags unless they are clearly part of the answer or explanation sections
- Maintain paragraph breaks, lists, tables, and other formatting

### Rule 5: Boundary Detection
The boundary between context and stem typically occurs at one of these markers:
- A question mark (`?`)
- Common interrogative phrases (see list below)
- A clear shift from narrative/descriptive content to interrogative content

## Exclusion Rules (Critical)

The following content must be **strictly excluded** from both `question_context_html` and `question_stem_html`:

### Excluded Content Types

1. **Answer Options**
   - Any content matching patterns: `A.`, `B.`, `C.`, `D.`, `E.`
   - Alternative patterns: `(A)`, `1.`, `Option A`, etc.
   - Full answer choice text and descriptions

2. **Explanations and Rationales**
   - Sections labeled "Explanation", "Rationale", "Discussion"
   - Educational content about why answers are correct or incorrect
   - Teaching points or learning objectives

3. **Metadata and Administrative Content**
   - Correct answer indicators (e.g., "Correct answer: B")
   - Peer performance statistics (e.g., "45% answered correctly")
   - Question IDs, source attributions
   - Difficulty ratings or classification tags

4. **Banned Phrases** (Partial List)
   - "Correct answer"
   - "The answer is"
   - "Explanation"
   - "Rationale"
   - "Educational Objective"
   - "Key Point"
   - "References"
   - "Peer Comparison"
   - "% answered correctly"

## Common Interrogative Phrases

The following phrases typically indicate the start of a question stem:

- "Which of the following"
- "What is the most"
- "What is the best"
- "What is the next"
- "What would you"
- "What should be"
- "How should"
- "Where is the"
- "When should"
- "Who is at risk"
- "Select the"
- "Choose the"
- "Identify the"
- "Determine the"

## Validation Requirements

### Structural Validation
- `question_stem_html` must not be empty
- `question_context_html` may be empty (empty string, not null)
- Both fields must contain valid HTML (or plain text)

### Content Validation
- No answer option patterns in either field
- No banned phrases in either field
- `question_stem_html` should contain either:
  - A question mark (`?`), OR
  - One of the common interrogative phrases listed above

### Semantic Validation
- The context should provide background without asking a question
- The stem should ask a specific question without providing contextual narrative
- Together, they should form a complete, answerable question

## Edge Cases

### Case 1: Question with Embedded Context
Sometimes a question embeds brief context within the interrogative statement itself:

> "In a patient with chest pain radiating to the left arm, which of the following is the most appropriate next step?"

**Handling:**
- If the embedded context is brief and integral to the question grammar, keep it in `question_stem_html`
- If it can be naturally separated, move the narrative portion to `question_context_html`

### Case 2: Multi-Part Questions
For questions with multiple sub-questions:
- Include the shared context in `question_context_html`
- Include only the primary interrogative in `question_stem_html`
- Sub-question parts are typically stored as separate question records

### Case 3: Tables, Figures, and Images
- Tables and figures that are part of the case presentation → `question_context_html`
- Tables/figures that are part of answer choices → EXCLUDE
- Image references should be preserved in the appropriate field

### Case 4: Ambiguous Boundaries
When the boundary between context and stem is unclear:
- Err on the side of including more in the context
- Ensure the stem remains clear and interrogative
- The stem should be readable and understandable given the context

## LLM Prompt Integration

When constructing an LLM prompt to perform this extraction:

1. Include this entire document or a summary of the key rules
2. Provide clear examples of correct splitting
3. Emphasize the exclusion rules to prevent leakage
4. Request output in the specific JSON format: `{"questions": [{"question_context_html": "...", "question_stem_html": "..."}]}`
5. Instruct the LLM to preserve HTML structure and formatting

## Version History

- **v1.0** (2025-11-23): Initial documentation of extraction rules for clean slate extraction pipeline

## Related Documentation

- `src/doughub/models.py`: Database schema definition
- `src/doughub/ui/dto.py`: `MinimalQuestion` and `MinimalQuestionBatch` DTO definitions
- `tests/test_ingestion.py`: Validation tests for extraction behavior
- `src/doughub/prompts/extract_minimal_question.llm.prompt`: LLM prompt file (to be created)
