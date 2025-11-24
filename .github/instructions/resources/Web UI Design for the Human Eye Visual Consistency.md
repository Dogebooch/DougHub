# Web UI Design for the Human Eye: Machine-Usable Guidelines

*(Distilled from “Principles of Visual Consistency” by UXPin)* 

---

## Core Principles

* **Design for expectations first, pixels second.**

  * User expectations = accumulated habits from other products (external consistency) + what they learn in your product (internal consistency).
* **Decide consistency rules *before* you draw UI.**

  * Do research and pattern decisions at the “features & flows” stage to avoid being biased by early mockups.
* **Use consistency to support, not kill, creativity.**

  * Reuse conventions for structure, navigation, and base components. Add originality in visuals, motion, and micro-interactions.
* **Consciously choose when to be inconsistent.**

  * Break expectations only when the benefit is clear (better goal completion, delight) and the deviation is learnable.

**Example**

* A news site keeps standard top nav, left-aligned logo, blue underlined links (consistency), but uses a bold, custom illustration style for article headers (originality).

---

## Layout

### Visual Flow

* **Optimize the first 50 ms impression.**

  * Users form “attractive vs ugly / simple vs complex / familiar vs unfamiliar” judgments almost instantly. Simple + familiar wins.
* **Create a clear reading path.**

  * Use size, alignment, and whitespace to guide eyes from primary CTA → supporting info → secondary actions.
* **Avoid unnecessary complexity.**

  * Fewer distinct layouts across screens; reuse grids and structures.

### Structural Rules

* Use a **consistent grid** across pages (columns, gutters, margins).
* Keep **related elements grouped**; separate unrelated groups with whitespace.
* Maintain **consistent padding** inside cards, buttons, and sections.
* Keep **search, profile, and account controls** clustered (often top-right) and styled consistently to indicate “secondary utilities.” 

**Example**

* Redhat uses card grids for “Technologies” and “Services & Support”:

  * Same card size and spacing across pages → scannable, consistent modules.
  * Search and account links are always top-right and grouped.

---

## Typography

### System

* **Limit the system** to ~2 font families (e.g., 1 for headings, 1 for body).
* **Define roles:** H1, H2, H3, body, meta, navigation, buttons, links.
* **Set each role once, reuse everywhere.**

Example CSS snippet (body text):

```css
body {
  font: 1em/1.5em Cambria, Arial, serif;
  color: #151;
}
```

### Rules

* **Vertical rhythm:** line-height ~1.4–1.6 × font size. Keep consistent for body copy. 
* **Alignment:** prefer left-aligned, ragged-right for paragraphs; keep alignment consistent per content type.
* **Headings:**

  * Increase size and/or weight as level rises (H1 > H2 > H3).
  * Use consistent case rules (e.g., title case for H1/H2, sentence case for H3).
* **Links:** consistent color and hover/active state (e.g., always underlined on hover).
* **Navigation text:**

  * Primary nav can be bold to signal importance.
  * Secondary nav can use all-caps with smaller size/weight.

**Example**

* UXPin redesign concept:

  * H1: large sans-serif with some words bolded.
  * Subhead: same family, regular weight, mixed case.
  * Primary nav: bold, mixed case.
  * Secondary nav: all caps, regular.
  * Body copy: left-aligned, ~1.6 line-height, generous margin above paragraphs.

---

## Color

### Palette

* **Choose a fixed palette**, then lock it in tokens (e.g., `primary`, `accent`, `danger`, `surface`, `text-muted`).
* Use **one dominant neutral** (background), **one primary**, and **limited accents**.
* Maintain **consistent roles**:

  * Primary actions = `primary` color.
  * Discount or emphasis tags = `accent`.
  * Destructive actions = `danger`.

### Behavior

* Keep **same color → same meaning** across app.
* Avoid mixing too many vivid colors; most screens should be neutral with focused accents.
* Ensure sufficient **contrast** between text and background for legibility.

**Examples**

* **Michael’s (art store)**:

  * Cream background + black logo and menus → stable neutral foundation.
  * Green consistently highlights promotions.
  * Red pops occasionally (search button, carousel locator) → draws attention but doesn’t overwhelm. 
* **Squarespace “Dreaming with Jeff” microsite**:

  * Dark backgrounds, white typography, and gold/yellow accents used repeatedly to create a nocturnal, cinematic feel.

---

## Components

### General Rules

* **Buttons**

  * Same border radius, padding, font, and shadow for all primary buttons.
  * Distinguish primary vs secondary:

    * Primary: filled.
    * Secondary: outline or muted color.
* **Cards**

  * Use equal height/width and spacing in grids.
  * Entire card should be clickable or only specific CTAs—pick one convention and stick with it.
* **Icons**

  * Use a single icon style (filled vs outline; stroke width; corner radius).
  * Apply consistent meaning to icon + color (e.g., green check = success everywhere).

### Spatial Rules

* Maintain **consistent padding/margins** inside and around components (e.g., 8/12/16/24 spacing scale).
* Use spacing to encode hierarchy:

  * Small gaps within a group.
  * Larger gaps between groups.

**Example**

* Redhat feature cards share: same icon style (white outline on red circle), same padding, same typographic hierarchy. This consistency makes scanning across pages effortless.

---

## Interaction Patterns

### Affordances & Signifiers

* **Affordance** = what the element can do.
* **Signifier** = visual cue that hints at that affordance. 
* Match **perceived affordance** with **actual affordance**:

  * Don’t reuse common icons (envelope, trash, play, gear) for unrelated functions.
* Use widely understood signifiers to reduce explanation:

  * Underlined blue text → link.
  * Caret/down arrow → expandable content.
  * Hamburger icon → menu.

### Pattern Types (Usage Level)

1. **Tactical patterns (atomic rules)**

   * Precise, black-and-white rules.
   * Examples: logo top-left; search top-right; link color; button sizes.
   * Codify them in a **style guide / design system** so developers reuse correctly.

2. **Strategic patterns (flow & UX choices)**

   * Chosen to support user goals and narrative.
   * Examples:

     * Single-page long scroll vs multi-page nav.
     * Hidden controls vs always-visible controls.
   * One strategic decision implies many tactical ones (scroll behavior, section breaks, CTA placement).

3. **Site-specific patterns (domain expectations)**

   * Patterns users expect purely from the **type of site**. 
   * Examples:

     * Agency/portfolio → gallery, case studies, testimonials pages.
     * Airline → booking form pattern (from/to, dates, passengers).
     * Ecommerce → product listing grid, product detail, cart, checkout.

### Example: Hidden Controls

* **Spotify**

  * Short context menu appears over an item (playlists/tracks) when invoked.
  * Shows only a few key options (Play, Add to Queue, Save).
* **Pinterest**

  * Hamburger icon opens a large mega-menu listing many categories.
  * Same core pattern (hidden menu), different strategic use: quick inline action vs global browsing.

### Selecting a Pattern (Algorithm)

1. **Identify the UX problem.**

   * E.g., users visit and browse but rarely sign up.
2. **Collect candidate patterns.**

   * E.g., lazy signup, signup incentives, social login. 
3. **Study implementations on other sites.**

   * Observe which services they connect, how they phrase labels, where they position controls.
4. **Specify your version.**

   * Define exact behavior, labels, layout, edge cases.
   * Document “Do/Don’t” examples.

**Social Login Example**

* Problem: users skip signup.
* Solution: social login pattern.

  * Support Facebook, plus 1–2 more networks common to your audience.
  * Place buttons next to traditional signup, within direct proximity to email/password fields.
  * Visual: labeled buttons with provider names + icons.
  * Ensure standard order (e.g., Facebook, then Google/Twitter).

---

## Navigation

### Pre-Design Research

1. **Card Sorting** (for IA and menu labels)

   * **Open sort**: users group unlabeled items and name groups; use when designing a new IA.
   * **Closed sort**: users sort into predefined groups; use when refining an existing structure.
   * Apply results to top nav, side nav, and category structure. 

2. **User Interviews**

   * Ask about **behaviors and workflows**, not UI jargon.

     * Bad: “Tabs or infinite scroll?”
     * Good: “How do you browse content? What frustrates you?”
   * Use answers to derive expectations: e.g., “distraction-free writing mode” implies hideable toolbars in your CMS.

3. **Heuristic Evaluation (Competitive Scan)**

   * Define fields: visual hierarchy, feedback, copy clarity, navigation ease, simplicity of input.
   * Score competitors, then visualize results (e.g., radar/spider chart).
   * Look for:

     * Where competitors are similar → potential *must-have* conventions.
     * Where they’re all weak → chance to outperform.

### Rules

* Use **global nav** patterns users already know (top bar, left sidebar, hamburger for small screens).
* Keep **nav labels literal**, mirroring user mental models surfaced in research.
* Provide **multiple paths** only when it genuinely reduces friction (e.g., both search and browse).

**Example**

* In redesigning Yelp (exercise in the book), closed card sorting revealed that users expected “Serves Dinner” to be first-level filter, not buried. Adjusting nav/filter IA to match expectations reduced friction.

---

## States & Feedback

*(The book touches this mainly via heuristics and pattern types.)*

* Ensure each interactive element has clear states:

  * default → hover → active/pressed → disabled → loading.
* Keep feedback **predictable and consistent**:

  * Same animation or highlight effect for “thing was added” events.
  * Same toast styling for system messages.
* Evaluate feedback during **heuristic reviews**:

  * Include “effectiveness of system feedback” as a scoring dimension. 

**Example**

* Incentive/gamification patterns like progress bars expose state: “Profile 70% complete” motivates continued use while making system status visible.

---

## Forms & Validation

*(Not a major focus in the book; guidelines here are inferred from patterns discussed.)*

* **Simplify input.**

  * Choose patterns (lazy signup, social login, minimal booking form) that reduce field count where possible.
* **Respect expectations for domain-specific forms.**

  * Airline: origin, destination, dates, passengers, class in a unified “flight search” module.
  * Don’t radically reorder this without strong evidence.
* **Order fields to match natural mental flow**, discovered via interviews or competitor heuristics.

---

## Error Handling

*(Only lightly implied; book focuses more on consistency than explicit error UX.)*

* Treat errors as **feedback patterns**: same layout, color, icon, and positioning across forms.
* Avoid surprises:

  * Don’t show error modals for actions that usually succeed silently.
  * Error text should be clear, not clever.

---

## Accessibility

*(Not explicit; only typography/contrast implications.)*

* Use **sufficient size and line height** for body text (no tiny fonts; ~1.4–1.6 line-height).
* Keep **high contrast** between text and background, especially on dark-themed sites (e.g., white text over dark imagery as in Squarespace’s microsite).
* Avoid relying on color alone to convey meaning; combine with icon or label.

---

## Content & Microcopy

* **Clarity over cleverness.**

  * Menu & button labels should match user mental models discovered through card sorting and interviews.
* Evaluate copy in heuristic reviews under “clarity of copy.”
* Keep **tone and terminology consistent** across pages:

  * If you call it “Projects” in nav, don’t call it “Boards” elsewhere unless there is a meaningful distinction.

**Example**

* Squarespace CTA buttons: primary is a short, direct action (“Listen”), secondary is also clear but visually demoted. Same style treatment reused across page sections.

---

## Motion

* Use motion to **reinforce**, not replace, structure.
* Establish a **baseline rhythm** with static repetition, then use motion as a deliberate break.

  * E.g., Neil Carpenter’s homepage has moving colored shapes that travel diagonally, forming a literal “visual flow” across an otherwise stable layout.
* Motion should:

  * Be consistent in easing and duration for similar actions.
  * Avoid distracting from primary tasks (e.g., subtle scroll-based parallax vs aggressive looping GIFs everywhere).

---

## Checklists

### Pre-Design Research Checklist

* [ ] Conduct card sorting (open or closed) to shape IA.
* [ ] Run interviews to understand workflows, habits, existing tools.
* [ ] Perform heuristic evaluation of competitors:

  * [ ] Visual hierarchy
  * [ ] Feedback & error handling
  * [ ] Copy clarity
  * [ ] Navigation ease
  * [ ] Simplicity of input
* [ ] Decide where to align with competitors vs intentionally differ.

### Visual Consistency Checklist

* **Typography**

  * [ ] ≤ 2 font families; roles explicitly defined.
  * [ ] Heading sizes/weights form clear hierarchy.
  * [ ] Body text line-height ~1.4–1.6 × font size.
  * [ ] Alignment and spacing consistent across pages.

* **UI Components**

  * [ ] Button styles (radius, padding, states) consistent.
  * [ ] Cards share dimensions and internal spacing.
  * [ ] Icons share style and meanings.
  * [ ] Images follow consistent treatment (size, crop, interaction behavior).

* **Color**

  * [ ] Palette defined as tokens (primary, accent, danger, surface, etc.).
  * [ ] Specific colors consistently map to roles (e.g., CTA, sale, error).
  * [ ] Contrast checked for text and key components.

* **Layout**

  * [ ] Shared grid and spacing scale across pages.
  * [ ] Related items grouped; unrelated items clearly separated.
  * [ ] Search and account utilities placed consistently.

### Pattern Selection Checklist

* [ ] Explicitly define the UX problem.
* [ ] List candidate patterns that solve similar problems.
* [ ] Review real-world examples of each pattern.
* [ ] Decide site-specific expectations first, then strategic, then tactical details.
* [ ] Document chosen pattern: layout, copy, states, and examples.
* [ ] Re-evaluate patterns periodically to avoid local maxima.

---

## Anti-Patterns

* Introducing **ads in a niche where none of the competitors use them**, causing jarring external inconsistency and user irritation. 
* Making **similar components behave differently** (e.g., some images open in a lightbox, others navigate away) with no visual distinction.
* Overusing different fonts, colors, or layouts per page so the product feels like unrelated microsites.
* Using icons or signifiers that **conflict with established meanings** (e.g., envelope logo on a non-mail product) and confusing perceived affordance.

---

## Examples (Design Recipes)

1. **Landing Page with Strong Visual Consistency**

   * Layout: hero section with central headline + primary CTA; secondary actions bottom-right; consistent grid below.
   * Typography: 1 display font for H1, 1 sans-serif for everything else.
   * Color: dark theme with white text + single accent color for buttons and progress indicators.
   * Components: CTA buttons all caps; secondary actions outlined; repeated usage down the page.

2. **Cards-Based Product / Feature Index**

   * Use uniform cards for each feature/product across all category pages.
   * Each card: icon → title → brief description → CTA.
   * Consistent hover behavior (e.g., shadow and slight scale).
   * Grid layout reused for different sections (“Technologies,” “Services & Support”).

3. **Social Login Module**

   * Place under or next to email/password fields.
   * Buttons labeled “Continue with [Provider]” with provider icons.
   * Providers ordered by popularity for your audience (often Facebook then Google/Twitter).
   * Same module used on signup, login, and upgrade flows.