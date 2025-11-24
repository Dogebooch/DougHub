# Design Systems Handbook (InVision) → Machine-Usable Guidelines

Source: *Design Systems Handbook* by Marco Suarez, Jina Anne, Katie Sylor-Miller, Diana Mounter, Roy Stanfield. :contentReference[oaicite:0]{index=0}

Book structure (for mapping):

- Introducing design systems (value, standards, components) :contentReference[oaicite:1]{index=1}
- Designing your design system (team, tokens, visual language, UI library) :contentReference[oaicite:2]{index=2}
- Building your design system (foundations, architecture, testing) :contentReference[oaicite:3]{index=3}
- Putting your design system into practice (rollout & adoption) :contentReference[oaicite:4]{index=4}
- Expanding your design system (vision, principles, process, voice & tone) :contentReference[oaicite:5]{index=5}

---

# Core Principles

## P1 — System over One-Offs

- Bespoke design is **slow, inconsistent, and hard to maintain**. :contentReference[oaicite:6]{index=6}
- A design system = **reusable components + clear standards** used to build many applications. :contentReference[oaicite:7]{index=7}
- Reusability is the core value: it enables scale, reduces design & technical debt, and speeds delivery. :contentReference[oaicite:8]{index=8}

**Operational rule:**

> Any new UI work must first ask: “Can we express this using existing tokens/components? If not, should the new pattern become part of the system?”

---

## P2 — Standards + Components

- **Standards** define the *what and why*: naming, accessibility, file structure, visual language (color, type, icons, space, motion). :contentReference[oaicite:9]{index=9}
- **Components** are reusable, code-backed building blocks (button → complex tables); simple, single-purpose components are more reusable. :contentReference[oaicite:10]{index=10}
- The system is “standards as rules” + “components as implementation” — both must evolve together.

---

## P3 — Design System Foundations (Katie Sylor-Miller)

A successful system is: :contentReference[oaicite:11]{index=11}

1. **Consistent** – predictable patterns for how components are built & managed.
2. **Self-contained** – lives in its own repo; consumed as a dependency.
3. **Reusable** – modular, composable, generic, flexible components. :contentReference[oaicite:12]{index=12}
4. **Accessible** – usable by as many people as possible (a11y baked into components). :contentReference[oaicite:13]{index=13}
5. **Robust** – well-tested, stable across products & platforms. :contentReference[oaicite:14]{index=14}

---

## P4 — Team & Governance

- Don’t treat the system as a side project; **staff it like a product**, not a project. :contentReference[oaicite:15]{index=15}
- Roles to involve: designers, front-end devs, a11y, content, research, performance, PM, and leadership champions. :contentReference[oaicite:16]{index=16}
- Team models (Nathan Curtis): :contentReference[oaicite:17]{index=17}
  - **Solitary** (“overlord”): fast but doesn’t scale; good for short-lived or political contexts. :contentReference[oaicite:18]{index=18}
  - **Centralized**: dedicated systems team; good maintenance, risk of disconnect from product research. :contentReference[oaicite:19]{index=19}
  - **Federated**: contributors from many product teams; high alignment but busy people. :contentReference[oaicite:20]{index=20}
  - Hybrid (Salesforce Lightning): central core + federation of core contributors across products. :contentReference[oaicite:21]{index=21}

**Guideline:** choose a centralized or hybrid/federated model for long-term scale; use solitary only as a bootstrap tactic.

---

## P5 — The System Is Never “Done”

- Myth: “Once the system is built, work is complete.”
- Reality: design systems are **living products**; teams must maintain and evolve them as needs change. :contentReference[oaicite:22]{index=22} :contentReference[oaicite:23]{index=23}

Operationalize this by:

- Versioning the system. :contentReference[oaicite:24]{index=24}
- Running retros after launches. :contentReference[oaicite:25]{index=25}
- Treating v1 rollout as **1.0**, not “final.” :contentReference[oaicite:26]{index=26}

---

# Layout (System-Level)

This book focuses on layout as *tokens + reusable layouts* rather than pixel-grids.

- Use the system to define layout primitives: spacing scale, breakpoints, layout components (grid, page shells, nav regions), not ad-hoc per page. :contentReference[oaicite:27]{index=27} :contentReference[oaicite:28]{index=28}
- In the UI library, classify components by level: elements, components, regions, layouts. :contentReference[oaicite:29]{index=29}
- Prefer layout components that:
  - Accept content slots/children.
  - Use tokenized spacing.
  - Work responsively by default (e.g., grid with breakpoint-based columns). :contentReference[oaicite:30]{index=30}

**Example classification:** :contentReference[oaicite:31]{index=31}

- Element: button, icon.
- Component: search form (icon + input + button).
- Region: sidebar nav, header.
- Layout: “dashboard layout” (header + sidebar + content + footer).

---

# Typography

The handbook uses typography mainly as part of the **visual language & tokens**.

- Use a small set of fonts: usually one primary + one monospace for code. More fonts → perf & consistency issues. :contentReference[oaicite:32]{index=32}
- Prefer legible, common faces or well-tested web fonts; set clear rules for headings/body and weights. :contentReference[oaicite:33]{index=33}
- Document:
  - Type scale (often modular, based on base 16px). :contentReference[oaicite:34]{index=34}
  - Line height (1.4–1.5× for body, tighter for headings) in accordance with WCAG. :contentReference[oaicite:35]{index=35}

Represent these as **design tokens** (e.g., `font-size-sm`, `line-height-heading`) so they can sync across platforms. :contentReference[oaicite:36]{index=36}

---

# Color

- Use color for:
  - Feedback (error, warning, success).
  - Information (charts, way-finding).
  - Hierarchy (structuring UI). :contentReference[oaicite:37]{index=37}
- Palette structure: :contentReference[oaicite:38]{index=38}
  - 1–3 brand primaries.
  - Shared action color for links & primary buttons.
  - Neutrals (grays) for backgrounds, borders.
  - Status colors (error/warn/success).
  - Optional object/product colors for way-finding (e.g., Salesforce object colors). :contentReference[oaicite:39]{index=39}
- Avoid huge uncontrolled tint/shade ranges that lead to inconsistency; offer a slim, intentional set, expand later if needed. :contentReference[oaicite:40]{index=40}

Again, express these as tokens (`color-primary-500`, `color-error-bg`) to ensure reuse. :contentReference[oaicite:41]{index=41}

---

# Components

## UI Inventory → Library

- **Step 1: Interface inventory.** Screenshot all in-production buttons, cards, lists, forms, etc., and group them to reveal duplication & inconsistency. :contentReference[oaicite:42]{index=42}
- **Step 2: Merge & rationalize.** Decide canonical variants, remove duplicates, record usage rules. :contentReference[oaicite:43]{index=43}
- **Step 3: Document components** with
  - Name
  - Description (when/why to use)
  - Examples
  - Code (markup + styles/JS)
  - Meta (status, release history) where useful :contentReference[oaicite:44]{index=44}

**Classification pattern (atomic-ish):**

- **Elements/basics/atoms** – buttons, icons.
- **Components/molecules/modules** – composed from elements (search form, card).
- **Regions/organisms/zones** – nav bars, headers, footers.
- **Layouts** – full-page compositions. :contentReference[oaicite:45]{index=45}

---

## Design Tokens (Sub-atomic Layer)

- Tokens are **name–value pairs** for design properties: colors, spacing, font sizes, radii, animation durations, etc. :contentReference[oaicite:46]{index=46}
- Example: `SPACING_MEDIUM: 1rem`, `RADIUS_SMALL: 2px`. :contentReference[oaicite:47]{index=47}
- Tokens are stored once and transformed for each platform (web, iOS, Android).

**Guideline:**

> No raw hex, px, or rem values in component code; always reference tokens.

---

## Code Architecture & Reuse

- Use modular, composable CSS patterns (SMACSS / OOCSS / BEM / CSS-in-JS). Key traits: :contentReference[oaicite:48]{index=48} :contentReference[oaicite:49]{index=49}
  - Clear naming for components, variants, and utilities.
  - Low CSS specificity, tightly scoped.
  - Utility classes for one-off tweaks built from tokens.
  - DRY: avoid duplicate code; share patterns instead. :contentReference[oaicite:50]{index=50}
- Namespace classes (`.ds-btn`) to avoid collisions with legacy CSS. :contentReference[oaicite:51]{index=51}

---

# Interaction Patterns (System-Level)

The book is tool & architecture focused; interaction specifics live in component docs.

**Patterns to capture per component:**

- States (default/hover/focus/active/disabled).
- A11y behavior (keyboard, ARIA roles, focus order). :contentReference[oaicite:52]{index=52}
- Usage rules (when to use button vs link, modal vs inline, etc.). :contentReference[oaicite:53]{index=53}

At system level, ensure:

- Components are generic enough to be reused in multiple flows. :contentReference[oaicite:54]{index=54}
- Utilities (spacing, typography) reduce “one-off CSS” and speed implementation. :contentReference[oaicite:55]{index=55}

---

# Navigation

- No specific IA patterns; navigation is treated as components/regions in the UI library.

Recommendations from examples:

- Use pilot projects with rich navigation (e.g., seller tools redesign at Etsy) to test navigation patterns and responsive layouts. :contentReference[oaicite:56]{index=56}
- Capture navigation shells (header, side nav) as reusable regions with documented variants.

---

# States & Feedback

Handled at component + system documentation level:

- Component docs must include all states, with code samples and a11y notes. :contentReference[oaicite:57]{index=57}
- Use system principles (see “Design principles” below) as **guards** when deciding how feedback should feel (calm vs loud, forgiving vs strict). :contentReference[oaicite:58]{index=58}

---

# Forms & Validation

Not deeply covered as UI patterns; treat forms as high-value components in your UI inventory:

- Inventory all existing forms & fields; identify common layouts and validation patterns. :contentReference[oaicite:59]{index=59}
- Codify:
  - Label placement rules.
  - Error message locations and tone.
  - Accessibility constraints (label–input association, hints, error announcements). :contentReference[oaicite:60]{index=60}

---

# Error Handling

Again, mostly delegated to component docs & a11y guidance:

- Document error states for components and flows; ensure they respect accessibility guidelines and use consistent language. :contentReference[oaicite:61]{index=61} :contentReference[oaicite:62]{index=62}

---

# Accessibility

Accessibility is treated as a **core property** of the system, not an afterthought.

- Make a11y enforcement part of the system:
  - Contrast-safe color tokens. :contentReference[oaicite:63]{index=63}
  - Keyboard & screen-reader-accessible components by default, using patterns like eBay’s MIND. :contentReference[oaicite:64]{index=64}
  - Document guidelines: larger text sizes, always-labeled form fields, alt text usage, etc. :contentReference[oaicite:65]{index=65}
- Use automated audits (AATT, a11y, aXe) as part of CI to catch regressions. :contentReference[oaicite:66]{index=66}

**Guideline:**

> Any new or changed component must pass automated a11y tests and manual keyboard/screen-reader checks before being marked “ready.”

---

# Content & Microcopy

Two key areas: **system docs** and **product voice & tone**.

## System docs

- “If it’s not documented, it doesn’t exist.” Docs prevent duplicate styles and failed adoption. :contentReference[oaicite:67]{index=67}
- Documentation must be:
  - Up-to-date (avoid doc debt, add tests to check doc changes with code). :contentReference[oaicite:68]{index=68} :contentReference[oaicite:69]{index=69}
  - Easy to find (good nav + search). :contentReference[oaicite:70]{index=70}
  - Practical (examples, tutorials, naming conventions, tooling notes). :contentReference[oaicite:71]{index=71}

## Voice & tone (product)

- The handbook highlights voice & tone as part of system alignment—especially as a dimension to **expand** the system beyond visuals. :contentReference[oaicite:72]{index=72}
- Document:
  - Principles for voice (e.g., clear over clever).
  - Examples of good vs bad microcopy.
  - Which system components need copy guidance (error messages, confirmations, empty states, etc.).

---

# Motion

- Motion is treated as part of the visual language and tokens (durations, easings).
- Example: IBM’s animation guidelines tie motions to product history and use cases, with named movement types. :contentReference[oaicite:73]{index=73}
- Document:
  - When motion is allowed/required (e.g., transitions, feedback).
  - Duration & easing tokens (e.g., `motion-fast`, `motion-default`).
  - Accessibility constraints (reduce motion mode).

---

# Putting the System into Practice (Rollout & Adoption)

## Rollout Modes

Two macro approaches: :contentReference[oaicite:74]{index=74}

1. **Large-scale redesign**

   - Design full system (tokens → components → page layouts) and roll it out with a big product redesign. :contentReference[oaicite:75]{index=75}
   - Benefits: cohesive result, clear “launch moment,” easier to align team.
   - Requires more up-front time & coordination.
2. **Incremental rollout**

   - Roll out slices of the system over time (e.g., utilities first, then components). :contentReference[oaicite:76]{index=76}
   - Benefits: less daunting, can start quickly, easier to test assumptions.
   - Requires strong communication; no single big launch to grab attention. :contentReference[oaicite:77]{index=77}

**Pilot project criteria** (Dan Mall, Etsy example): pick a pilot that has reusable components, high-value elements, technical feasibility, a strong champion, and achievable scope. :contentReference[oaicite:78]{index=78}

---

## Adoption Tactics

### Training & Sandboxes

- Give designers and devs **sandbox environments** mirroring production CSS so they can prototype without writing new CSS. :contentReference[oaicite:79]{index=79}
- Provide tutorials for:
  - Using utilities vs components.
  - Building responsive layouts.
  - Real flows (e.g., search results page). :contentReference[oaicite:80]{index=80}

### Documentation & Findability

- Document styles as you add them; treat this as part of definition of done. :contentReference[oaicite:81]{index=81}
- Improve navigation & search so people can find patterns without pinging maintainers. :contentReference[oaicite:82]{index=82}

### Collaboration Creates Champions

- Create cross-functional working groups to evolve the system (designers, engineers, PMs, specialists). :contentReference[oaicite:83]{index=83}
- People who contribute become **system evangelists**; widen contributions beyond the core team as soon as you can. :contentReference[oaicite:84]{index=84}

### Post-Rollout Research

- After launch, run sessions with:
  - Contributors – understand onboarding pain points. :contentReference[oaicite:85]{index=85}
  - Engineering early adopters – find doc gaps, tooling needs. :contentReference[oaicite:86]{index=86}
  - PMs – clarify impact on scope & responsiveness. :contentReference[oaicite:87]{index=87}
- Use these insights to refine docs, training, and component coverage. :contentReference[oaicite:88]{index=88}

### Open vs Internal Docs

Pros of **public** docs: recruiting signal, community contributions, visibility of team maturity. :contentReference[oaicite:89]{index=89}
Cons: auth friction for externals, overhead handling community input. :contentReference[oaicite:90]{index=90} :contentReference[oaicite:91]{index=91}

---

# Expanding Your System (Vision, Principles, Process)

Once components are in place, expand alignment across **why, how, and voice**. :contentReference[oaicite:92]{index=92}

## Vision

- A vision statement is your **North Star**, describing what you want to achieve and why it’s worth it (e.g., Starbucks’ “We create digital products that make our customers happy and our partners proud”). :contentReference[oaicite:93]{index=93}
- Vision clarifies what matters and makes non-essentials easier to cut. :contentReference[oaicite:94]{index=94}

**Exercise:** describe where your team/product should be in 2–5 years; check if today’s work ladders up. If not, adjust direction. :contentReference[oaicite:95]{index=95}

## Design Principles

- Teams grow → implicit taste standards break down; explicit **design principles** become critical. :contentReference[oaicite:96]{index=96}
- Principles:
  - Provide guardrails for evaluating work.
  - Replace subjective arguments with shared language. :contentReference[oaicite:97]{index=97}
  - Explain how the system should be used. :contentReference[oaicite:98]{index=98}

Creation process: collect raw inputs from the team (interviews, surveys), then combine & refine into a distilled set that meets explicit goals (who they help, how they’re used, output vs process). :contentReference[oaicite:99]{index=99}

Make principles visible—on walls, in the system site, in critique language—so disagreements drop because you’re “now aligned.” :contentReference[oaicite:100]{index=100}

## Process

- Provide a consistent UX process as another layer of the system. Benefits: :contentReference[oaicite:101]{index=101}
  1. Clear expectations at each step.
  2. Data collection per step to inform iterations.
  3. Clarity on roles & responsibilities.
  4. Smooth, predictable progress & better quality.

InVision’s 6-step process example (summarized): understand → explore → [subsequent steps continue: design, validate, build, iterate]. :contentReference[oaicite:102]{index=102} :contentReference[oaicite:103]{index=103}

---

# Checklists

## Design System Creation Checklist

- [ ] Team assembled with design, FE, a11y, content, research, performance, PM, leadership. :contentReference[oaicite:104]{index=104}
- [ ] Team model chosen (centralized / federated / hybrid) & documented. :contentReference[oaicite:105]{index=105}
- [ ] Interviews run with:
  - [ ] Internal consumers (designers, devs, PMs). :contentReference[oaicite:106]{index=106}
  - [ ] Possibly open-source community (if system will be public). :contentReference[oaicite:107]{index=107}
  - [ ] Executives/leadership for goals & metrics. :contentReference[oaicite:108]{index=108}
- [ ] Visual inventory done (colors, type, spacing, images). :contentReference[oaicite:109]{index=109}
- [ ] UI inventory done (elements, components, regions, layouts). :contentReference[oaicite:110]{index=110}
- [ ] Design tokens defined for color, type, spacing, motion, etc. :contentReference[oaicite:111]{index=111}

## Implementation Checklist

- [ ] System repo created, separate from product repos; published via package manager with versioning. :contentReference[oaicite:112]{index=112} :contentReference[oaicite:113]{index=113}
- [ ] Code style guide completed (CSS/JS), linting & editor config in place. :contentReference[oaicite:114]{index=114} :contentReference[oaicite:115]{index=115}
- [ ] Modular CSS architecture defined (naming, utilities, specificity rules). :contentReference[oaicite:116]{index=116}
- [ ] Automated tests:
  - [ ] Unit
  - [ ] Functional
  - [ ] Visual regression
  - [ ] Automated a11y :contentReference[oaicite:117]{index=117}

## Rollout & Adoption Checklist

- [ ] Rollout mode chosen (large-scale vs incremental) with documented rationale. :contentReference[oaicite:118]{index=118} :contentReference[oaicite:119]{index=119}
- [ ] Pilot project selected using scorecard (reuse potential, business value, feasibility, champion, scope). :contentReference[oaicite:120]{index=120}
- [ ] Style guide site live with:
  - [ ] Component & utility docs.
  - [ ] Nav structured for findability, not just package structure. :contentReference[oaicite:121]{index=121}
  - [ ] Search implemented. :contentReference[oaicite:122]{index=122}
- [ ] Training sessions & sandboxes provided. :contentReference[oaicite:123]{index=123}
- [ ] Feedback loops set up:
  - [ ] Contributor onboarding research. :contentReference[oaicite:124]{index=124}
  - [ ] Early-adopter sessions (engineers, PMs). :contentReference[oaicite:125]{index=125} :contentReference[oaicite:126]{index=126}

## Expansion Checklist

- [ ] Vision statement written and socialized. :contentReference[oaicite:127]{index=127}
- [ ] Design principles created, documented, and surfaced in critiques. :contentReference[oaicite:128]{index=128} :contentReference[oaicite:129]{index=129}
- [ ] UX process defined, with named stages and deliverables. :contentReference[oaicite:130]{index=130}
- [ ] Voice & tone guidelines integrated into the system docs. :contentReference[oaicite:131]{index=131}

---

# Anti-Patterns

- Treating the design system as a **one-off project**, not an evolving product. :contentReference[oaicite:132]{index=132}
- Over-relying on a solitary “overlord” maintainer; doesn’t scale. :contentReference[oaicite:133]{index=133}
- Building docs in a totally separate, hand-maintained codebase → immediate doc rot. :contentReference[oaicite:134]{index=134}
- Duplicating components to avoid breaking changes (“Tabs” vs “Tabs2”) instead of using versioning. :contentReference[oaicite:135]{index=135}
- Releasing undocumented styles/components (“If it’s not documented, it doesn’t exist”). :contentReference[oaicite:136]{index=136}
- Ignoring accessibility until late → expensive retrofits and legal risk. :contentReference[oaicite:137]{index=137}

---

# Examples

## Example: Button Component (System View)

- **Tokens used:** `color-action-default`, `spacing-sm`, `radius-sm`, `font-weight-semibold`. :contentReference[oaicite:138]{index=138}
- **Variants:** primary, secondary, destructive, ghost.
- **States:** default, hover, focus (visible outline), active, disabled.
- **Docs include:** usage rules (when not to use as navigation), a11y (ARIA, keyboard triggers), and code snippet.

## Example: Pilot Project — Etsy Seller Tools

- Used seller tools redesign as a pilot to:
  - Test new visual styles & CSS approach.
  - Build a new style guide alongside a real product area. :contentReference[oaicite:139]{index=139}
- Evaluated success using criteria like reuse potential, business value, feasibility, champion availability, and scope. :contentReference[oaicite:140]{index=140}

---

# References (from the book)

You can explore these from the original handbook as deeper resources:

- Styleguide / design-system collections (Anna Debenham, Brad Frost). :contentReference[oaicite:141]{index=141}
- CSS architecture & front-end design system books. :contentReference[oaicite:142]{index=142}
- Tokens in design systems, accessibility resources, and performance checklists. :contentReference[oaicite:143]{index=143} :contentReference[oaicite:144]{index=144}

Use this distilled spec as the operational layer in your tooling (VS Code, notebooks, Anki, etc.); go back to the PDF for detailed narratives and case studies when needed. :contentReference[oaicite:145]{index=145}
