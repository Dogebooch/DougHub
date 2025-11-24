# Web UI Design for the Human Eye - Part 2

## Z-Pattern Layout (Focused, Simple Pages)

Use for: minimal homepages, campaign pages, simple product/marketing pages with one main CTA.

### How the Z-pattern works

* User eye path:
  1. **Point 1 (top-left):** start (often logo).
  2. Scan horizontally to  **Point 2 (top-right)** .
  3. Diagonal scan across the center (hero area).
  4. Horizontal scan from **Point 3 (bottom-left)** to  **Point 4 (bottom-right)** .

### Layout Rules

* **Point 1 (top-left):**
  * Logo or primary brand marker.
* **Top bar (1 → 2):**
  * Simple nav, maybe a minor CTA (“Log in”, “Help”).
  * Keep nav light; avoid overwhelming the main CTA below.
* **Diagonal/center area:**
  * Use a hero section that pulls the eye down and across:
    * Strong headline + supporting subheadline.
    * Hero image / illustration, or short explainer.
  * Ensure composition subtly points toward the bottom CTA (e.g., visual lines, character gaze, arrow, device orientation).
* **Bottom row (3 → 4):**
  * Place the **primary CTA at Point 4** (e.g., “Get Started”, “Sign Up”).
  * Use the row to list key benefits or secondary links that guide scanning toward the primary CTA.
* **Background:**
  * Keep calm and unobtrusive; the pattern itself must be the star, not the backdrop.
* **Extended Z (repeating):**
  * For longer pages, stack multiple Z-shaped sections:
    * Each “Z” presents a value proposition and ends in a CTA or link.
    * Maintain a clear visual rhythm: value → support → CTA.

# Typography

## Role of Typography

* Typography has  **two channels of meaning** :
  * The literal wording.
  * The visual tone: size, weight, case, spacing, color, and position.
* You are always communicating with *both* channels; design them intentionally.

## Context: Audience & Message

* **Audience (personas):**
  * Use user personas to validate typographic choices:
    * Are they likely to read an ornate script as “luxury” or “hard to read”?
    * Does a Gothic font feel “fashionable and edgy” or “old-fashioned and serious”?
* **Type of message:**
  * Ask: “Is this for a product pitch, navigation, legal text, microcopy, error message…?”
  * Make typography align with  *purpose* :
    * Banking homepage → straightforward, trustworthy sans-serif.
    * Campaign microsite → same font but larger, bolder, brighter to feel human and friendly.
    * Youth brand → modern and energetic, but not childish.

### Example Pattern: Reusing One Typeface in Different Contexts

* **Main site:**
  * Sans-serif at moderate size, standard weight, conservative green.
  * Effect: calm, reliable, “serious institution.”
* **Campaign microsite:**
  * Same sans-serif, larger and bolder, brighter green, more breathing room.
  * Effect: personal, human, conversational.

## Combining Copy and Typography

* When authoring text, consider:
  * **Length:** Short words make punchy headlines; long phrases need more space and calmer styling.
  * **Sound & rhythm:** Repetition and rhyme can complement bold or playful type.
  * **Shape:** Certain letter combinations create visually pleasing silhouettes at large sizes.

## Legibility (Character-level)

* Use decorative typefaces *sparingly* for display only (e.g., one-word headlines, logos).
* For long-form content:
  * Prefer clean serif or sans-serif body fonts with high legibility.
* Reduce cognitive load:
  * Avoid overly ornamental scripts for anything that must be read rather than merely noticed.
* Don’t let the typeface compete with the content:
  * Styling should support reading, not show off.

## Readability (Paragraph-level)

* **Measure (line length):**
  * Aim for **~60–70 characters per line** for body text.
* **Line height:**
  * Use **1.3–1.5** line height (CSS `line-height`) to avoid cramped text.
* **Alignment:**
  * Left-align body text for most interfaces.
  * Avoid full justification for web content; it introduces awkward gaps and reduces readability.
* **Color & contrast:**
  * Ensure high enough contrast between text and background.
  * Slightly lighter text on a very dark background can reduce glare.
* **Role-based font pairing:**
  * Use a display font for headings and a highly readable font for body content and microcopy.

## Hierarchy Levels

Implement at least three levels:

1. **Primary (Level 1)**
   * Use for: page title, key headline, or major callout.
   * Traits:
     * Largest size on page.
     * Strong weight (often bold).
     * Positioned near top-left or in focal zone.
     * May use a distinct color vs. other text.
2. **Secondary (Level 2)**
   * Use for: section titles, subheads, captions, pull quotes.
   * Traits:
     * Smaller than primary, larger than body.
     * Style variations: italics, different color, or weight.
     * Visibly distinct but not overpowering.
3. **Tertiary (Level 3 – body text)**
   * Use for: main content paragraphs.
   * Traits:
     * Consistent size and color.
     * Minimal decoration.
     * Designed for immersion, not attention-grabbing.
4. **Micro-hierarchy (Level 4+)**
   * Use within paragraphs:
     * Emphasis via  **bold** ,  *italic* , subtle color changes, or links.
   * Use sparingly to avoid “noise.”

---

## Typographic Control Variables

Use these levers to encode hierarchy and tone:

* **Size:** Primary control for prominence.
* **Weight:** Bolder = closer to foreground (but don’t overuse bolding).
* **Italics:** Medium emphasis; good for emphasis in body text, quotes, or secondary labels.
* **Capitalization:**
  * ALL CAPS feels loud/urgent; use only when you intend that.
  * Title case or sentence case is generally softer and more readable.
* **Color:**
  * Warm colors (red/orange/yellow) jump forward; cool colors recede.
  * Use color sparingly to mark actions, links, or key data.
* **Contrast (between styles):**
  * Use contrast (size, weight, typeface) to create clear visual differences between levels.
* **Space:**
  * Add whitespace around important text blocks.
  * Increase padding/margins for headlined sections to signal structure.
* **Position:**
  * Early in reading order (top-left in LTR languages) = more attention.
* **Orientation:**
  * Tilted or vertical text grabs attention; reserve for special labels, not body copy.
* **Texture (pattern of text blocks):**
  * Vary block length and density to create a pleasing “texture.”
  * Break patterns with a contrasting block to highlight something important.

---

# Color

*(Only as it relates to typography and layout in this book.)*

* Use color to:
  * Differentiate levels of hierarchy (e.g., darker headline, slightly softer body text).
  * Draw attention to CTAs and important numbers (e.g., phone number in header).
* Control contrast:
  * High-contrast foreground/background for text readability.
  * Avoid overly busy or high-saturation backgrounds behind copy.
* Warm vs. cool:
  * Warm, saturated colors naturally attract more attention; use them for CTAs or highlights.
  * Cool or muted colors recede and are suitable for background or secondary items.

---

# Components

From the book, key component patterns are:

* **Global header / navigation bar:**
  * Top horizontal bar with logo (left) and nav links (right).
  * May include phone numbers, login, and minor CTAs in F- or Z-pattern.
* **Sidebar:**
  * Right-hand column for ads, related content, search, popular posts, categories.
  * Secondary to the main content column.
* **Hero section (Z-pattern):**
  * Large title, subheading, supportive image, and supporting CTA(s).
* **Feature rows / cards:**
  * Repeated horizontal blocks representing articles, products, or features.
* **Call-to-action blocks:**
  * Designed as endpoints of scan paths (end of F rows or at Point 4 in Z).
  * Clear, high-contrast button or link; minimal surrounding clutter.

---

# Interaction Patterns

* **Scanning behavior:**
  * Assume scanning as default; design to be understood from glimpses, not full reading.
* **Hooks and entry points:**
  * Put critical information and keywords at the start of lines, headings, and paragraphs.
* **Calls-to-action:**
  * Align CTAs with natural eye pause points:
    * End of F rows (top-right, card ends).
    * Z-pattern endpoints (top-right as minor, bottom-right as primary).
* **Content modularity:**
  * Construct pages from content modules (rows, cards, hero blocks) that support scanning patterns.

---

# Navigation

* Prefer **top horizontal navigation** aligned to F/Z patterns:
  * Logo left, navigation center/right, utility links or minor CTA far right.
* Keep labels short and descriptive; front-load keywords.
* Include search or category tools in sidebar for content-heavy layouts.

---

# States & Feedback

* Not explicitly detailed in this book.
* Indirect guidance:
  * Any state messaging (e.g., success/failure, notices) should use typography that clearly communicates priority and tone (strong but readable, not decorative).

---

# Forms & Validation

* Not explicitly covered.
* Implicit hints:
  * Any form labels, validation messages, or help text should follow readability rules:
    * Adequate contrast.
    * Clear hierarchy between label, input, and helper/error text.

---

# Error Handling

* Not explicitly covered.
* However:
  * Error messages should use typography that signals importance without sacrificing readability (e.g., clear bold label, red accent, but body text still well-spaced and legible).

---

# Accessibility

* Accessibility is not addressed directly, but the typography rules support it:
  * Adequate contrast, readable line lengths, proper line spacing.
  * Avoid overly decorative fonts for essential content.
* Avoid layouts that hide important actions in visually weak positions (e.g., tiny CTAs in low-contrast areas).

---

# Content & Microcopy

## Content-First Approach

* Start content work **in parallel** with early design:
  * Even rough “proto-content” is better than lorem ipsum.
* Accept imperfect early copy; refine later, but use it to:
  * Reveal layout issues early (too-long titles, multi-line labels).
  * Drive decisions about hierarchy and scan paths.

## Proto-content Strategies

1. **Write it yourself (designer writing draft copy):**
   * Write simple, clear stand-in copy per component.
   * Use it to stress-test layout (especially long names, unusual dates/times).
2. **Use existing site content (for redesigns):**
   * Copy over real text from the current site and design around genuine content.
3. **Use competitors’ content as a smart placeholder:**
   * Copy similar patterns, change names/places, and later replace with your own.
   * Helps understand how others solved similar messaging/layout problems.

## Copy for Scanning

* Place the most important information:
  * In the first two content sections.
  * At the beginning of headlines and paragraphs.
* Use:
  * Short paragraphs focusing on a single idea.
  * Bulleted lists where possible.
* Ensure CTAs and key value props sit in `Point 2 / 4` positions of F/Z patterns.

---

# Motion

* Not directly covered.
* Indirect implication:
  * If animation is used, it should support scanning (e.g., subtle movement in hero to pull eyes along the Z diagonal), not distract from content.

---

# Checklists

## Layout & Scanning Checklist
