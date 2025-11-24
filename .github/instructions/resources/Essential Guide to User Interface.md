# *he Essential Guide to User Interface Design* (Galitz)

Audience: engineers, designers, and AI agents implementing UI.

---

## Core Principles

- **Usability and utility**

  - Design for both: the product must solve real tasks (utility) and be efficient, learnable, and satisfying (usability).
  - Measure usability with: effectiveness, efficiency, error rate, learnability, and satisfaction.
- **Clarity**

  - Make visuals, concepts, and language unambiguous.
  - Prefer plain language over jargon; avoid technical or system-internal terms.
  - Show only information needed to decide or act on the current step.
- **Consistency**

  - Keep locations, interaction patterns, wording, fonts, colors, and icon meanings consistent across screens.
  - Reuse patterns instead of inventing new ones per feature.
- **Feedback**

  - Every user action should have a clear, timely reaction: visual, textual, or auditory.
  - Show system status for long operations and background work.
  - Preserve user work whenever possible.
- **Accessibility**

  - Design for perceptible, operable, understandable, and forgiving experiences.
  - Support keyboard-only use, assistive tech, high-contrast modes, and scalable text.
  - Avoid relying on color alone to convey meaning.
- **Aesthetics**

  - Favor simple, clean layouts with strong alignment, grouping, and adequate white space.
  - Limit palette and typefaces; visual polish improves perceived ease of use.
- **AI-specific: Trust, transparency, and control**

  - Make it obvious when content is AI-generated or AI-modified.
  - Communicate limitations: possible errors, out-of-date knowledge, or approximations.
  - Give users clear controls to:
    - Inspect (see sources, reasoning, or context when appropriate).
    - Revise (edit prompts, tweak instructions).
    - Revert (undo AI changes, restore previous state).
- **AI-specific: Uncertainty and safety**

  - Prefer honest partial answers over confident but incorrect ones.
  - Expose uncertainty when material: labels such as `Low confidence` or `May be incomplete`.
  - Apply stricter patterns for safety-sensitive domains (health, finance, legal).

---

## Layout

- **General**

  - Keep related elements close; group with spacing, alignment, or containers.
  - Place primary content and actions near the top; secondary items lower or in side panels.
  - Maintain a top-to-bottom, left-to-right reading flow where possible.
  - Avoid visual clutter: limit simultaneous visible elements and avoid unnecessary ornamentation.
- **Grid and spacing**

  - Use a consistent grid system and spacing scale (for example: 4 px or 8 px base).
  - Maintain consistent margins and gutters between groups and components.
  - Ensure enough white space for scanability; avoid dense, cramped layouts.
- **Control placement**

  - Place frequently used and primary controls near the top-left or top of the interaction area.
  - Put commit or finalizing actions (for example, `Save`, `Submit`) at the bottom or right edge of the workflow region.
  - Place controls that enable or affect others above or to the left of the controls they affect.
- **Page length (web)**

  - Keep critical information and primary actions within the first screenful (top segment of the page).
  - Shorter pages for navigation hubs and overview pages.
  - Longer pages for reading and continuous content, but keep structure through headings and anchors.
  - Avoid horizontal scrolling.
- **AI-specific: Multi-panel layouts**

  - Common AI layout:
    - Left: context (files, settings, prompts, history, filters).
    - Center: primary content or conversation.
    - Right: details (sources, options, parameters, logs, or diff).
  - Keep context panel visible when AI behavior depends on attached content; clearly list what is in scope.
- **AI-specific: Chat layout**

  - Show messages in a vertical stream: user, assistant, system messages clearly differentiated.
  - Keep input box anchored at bottom with clear affordances.
  - Provide a clear boundary between old and new responses (for example, scroll-to-bottom indicator).

---

## Typography

- **Font selection**

  - Use readable, simple fonts (sans-serif is usually best on screens).
  - Use mixed case for text; avoid ALL CAPS body text.
  - Limit the number of typefaces (usually 1–2 families with a small set of weights).
- **Sizing and hierarchy**

  - Provide clear typographic hierarchy: title > section heading > subheading > body > caption.
  - Typical on-screen ranges:
    - Body: about 14–18 px.
    - Headings: 1.25–2.0× body size.
  - Use weight, size, and spacing instead of color alone for emphasis.
- **Line length and spacing**

  - Keep line length moderate (about 50–100 characters per line).
  - Use adequate line height to prevent crowding; typically 1.4–1.6× font size.
  - Separate paragraphs with space; avoid walls of text.
- **Microcopy style**

  - Sentences under ~20 words when possible.
  - Short paragraphs (under 6 sentences).
  - Prefer active voice, affirmative phrasing, and chronological order.
- **AI-specific**

  - Make AI-generated text highly scannable: headings, bullets, and short paragraphs by default.
  - When the user requests a strict format (for example, JSON, table, outline), keep typography simple and avoid decorative inline formatting.
  - Expose options for verbosity (short / medium / detailed) near the input or result.

---

## Color

- **General**

  - Use a small palette: usually 1–2 neutrals, 1 primary, 1–2 accent colors.
  - Ensure sufficient contrast for text and critical UI elements.
  - Choose background colors first; derive foreground colors from them.
  - Avoid low-contrast combinations or color pairings that are hard for color-deficient users.
- **Semantic usage**

  - Use color consistently to encode meaning (for example:
    - Neutral: default elements and chrome.
    - Blue or equivalent: links, primary actions.
    - Green: success or positive states.
    - Yellow / amber: warnings.
    - Red: errors, destructive actions.)
  - Do not use color as the only indicator of state; pair with icons, labels, or patterns.
- **Visual restraint**

  - Limit colored elements in dense textual or data-heavy views.
  - Use color to emphasize the most important content, not decoration.
- **AI-specific**

  - Use subtle but consistent color cues to identify:
    - AI-generated content.
    - User-authored content.
    - Original vs edited content (for example, subtle highlights in the margin).
  - For risk or uncertainty indicators, use clear text labels in addition to color.
  - Avoid alarmist coloring for routine uncertainty; reserve strong colors (like solid red banners) for true errors or safety issues.

---

## Components

- **Labels and captions**

  - Place labels close to their controls (top or left alignment).
  - Use clear, task-oriented names; avoid internal codes or database field names.
  - Use consistent capitalization (for example, sentence case or title case).
- **Text inputs and editors**

  - Distinguish single-line vs multi-line fields visually.
  - Include placeholder text for hinting format or example, not for essential labels.
  - Maintain clear focus states.
- **Buttons and actions**

  - Make primary actions visually distinct from secondary actions.
  - Use verbs that describe outcomes (for example, `Send`, `Save`, `Summarize`).
  - Keep destructive actions visually separated and clearly labeled.
- **Selection components**

  - Use radio buttons for mutually exclusive small sets.
  - Use checkboxes for independent toggles.
  - Use dropdowns only when space is constrained or options are numerous.
- **AI-specific components**

  - Response cards:
    - Treat each response as a card with metadata (time, source, model, confidence if available).
    - Include quick actions: `Regenerate`, `Refine`, `Shorten`, `Explain`, `Copy`.
  - Context chips:
    - Represent attached files, selected datasets, or constraints as removable chips.
    - Show them near the input or at the top of the conversation.
  - Diff views:
    - For AI edits, offer side-by-side or inline diff views.
    - Provide a one-click `Revert` and a way to copy either version.

---

## Interaction Patterns

- **Menus and navigation patterns**

  - Use menus for discoverability; keep structures shallow and logical.
  - Group related actions; avoid overlong menus.
  - Provide accelerators and shortcuts for expert users.
- **Search**

  - Keep a simple search field easily available in content-heavy experiences.
  - Indicate search scope (for example, this page, this project, all workspaces).
  - Offer helpful error and empty-result messages, plus suggestions or filters.
- **AI prompt-to-response loop**

  - Standard pattern:
    1. User enters a prompt or modifies a preset.
    2. System shows a clear `Thinking` or `Generating` state.
    3. System streams or returns the response.
    4. User refines through follow-up prompts or quick actions.
  - Treat every new response as building on visible context; indicate when context is limited or has changed.
- **Mixed-initiative behavior**

  - The AI may:
    - Ask clarification questions when the user request is ambiguous or under-specified.
    - Offer suggestions or templates that the user can accept or modify.
  - Ensure AI questions are:
    - Few, focused, and clearly justified.
    - Easy to skip when not needed.
- **AI presets and tools**

  - Provide clear, named presets for common tasks (for example, `Summarize`, `Explain`, `Translate`, `Improve writing`).
  - Allow users to customize and save frequent workflows as reusable recipes.

---

## Navigation

- **Global navigation**

  - Keep primary navigation visible and consistent across main screens.
  - Use clear labels instead of internal project or feature names.
  - Avoid deep hierarchies when frequent switching is expected.
- **Local navigation within tasks**

  - Use clear steps or sections when tasks span multiple screens.
  - Indicate progress and allow safe backtracking without losing data.
- **Sessions and history**

  - Treat each conversation or project as a named unit.
  - Enable:
    - Listing, searching, and filtering sessions.
    - Reopening old sessions with context intact.
  - Show when new actions will start a new session vs continue an existing one.
- **AI-specific: Context and scope**

  - Display active context near the interaction area:
    - Files or datasets in scope.
    - System instructions or persona.
    - Relevant settings (for example, tone, style, audience).
  - Provide a clear way to adjust or reset context.

---

## States & Feedback

- **Basic states**

  - Idle: ready for input, controls clearly enabled or disabled.
  - Input in progress: show caret, focus, and any live validation.
  - Processing: show progress or busy indicators.
  - Completed: display results and follow-up options.
- **Feedback requirements**

  - Feedback should be timely:
    - Immediate for simple actions (clicks, toggles).
    - Progressive for long operations (progress bars, status messages).
  - Avoid leaving the user uncertain about whether the system is working.
- **AI-specific: Thinking and generation**

  - Show distinct states for:
    - Queued (for example, `In queue…`).
    - Processing (for example, `Analyzing document…`).
    - Generating output (for example, `Writing answer…`).
  - For responses longer than a brief moment to compute, show a skeleton or streaming output.
  - Allow user to cancel long-running generations.
- **AI-specific: Uncertainty and confidence**

  - Indicate low confidence or partial coverage with concise labels and optional explanations.
  - Provide access to sources or evidence when available (`Show sources` action).
  - Suggest next steps when the answer may be incomplete (for example, `You may want to verify this with X`).
- **AI-specific: Source attribution**

  - When responses rely on external material:
    - Show citations or links near relevant sections.
    - Provide a compact list of sources at the end of the answer.
    - Make it easy to inspect and open sources without losing context.

---

## Forms & Validation

- **Structure**

  - Group fields into logical sections of about 5–7 related items.
  - Place required and frequently used fields earlier and near the top.
  - Clearly indicate required fields and explain any non-obvious constraints.
- **Labels and instructions**

  - Put instructions before the controls they refer to.
  - Use helper text for format hints and inline explanations.
  - Avoid long instructional paragraphs; use bullets for rules.
- **Validation timing**

  - Use inline, near-field validation for most conversational and web forms.
  - Avoid interruptive dialogs for simple validation issues.
  - For high-speed data entry, validate on submit but highlight all issues together.
- **Error presentation**

  - Highlight fields with errors using color plus icon or text.
  - Display messages in context (near the field) and optionally in a summary at the top.
  - Keep the user’s input; never force re-entry of all fields.
- **AI-specific**

  - AI-assisted form filling:
    - Allow users to accept or reject suggested values explicitly.
    - Show where values came from (for example, extracted from a document).
  - For AI-generated text fields (descriptions, summaries):
    - Mark them as AI-generated.
    - Let users easily edit and store their final versions.
    - Avoid overwriting user-entered text without confirmation.

---

## Error Handling

- **Principles**

  - Prevent errors where possible through constraints and clear instructions.
  - When errors occur:
    - Preserve user work.
    - Clearly explain what happened and how to fix it.
  - Avoid blame, scolding language, or ambiguous jargon.
- **Message content**

  - State:
    1. What went wrong.
    2. Why it matters (if needed).
    3. What the user can do about it.
  - Keep messages concise and specific to the context.
- **Recovery**

  - Offer clear recovery actions (for example, `Retry`, `Edit input`, `Use defaults`, `Cancel`).
  - Avoid dead ends; users should always have a safe path forward.
- **AI-specific: Technical failures**

  - For timeouts, capacity issues, or connectivity problems:
    - Explain that the system had a problem, not the user.
    - Offer to retry or modify the request.
    - Keep the original input visible and editable.
- **AI-specific: Content-quality issues**

  - Provide a way to report:
    - Inaccuracy or hallucination.
    - Harmful or inappropriate content.
    - Irrelevant or off-topic output.
  - Use this feedback to refine models or guardrails (internally), not to block the user from continuing normal work.
- **AI-specific: Edits and reversibility**

  - For any AI-driven change to user content:
    - Provide a before/after view or a diff.
    - Make it easy to revert or partially accept changes.
    - Avoid applying irreversible transformations without an explicit confirmation.

---

## Accessibility

- **General**

  - Support keyboard navigation for all interactive elements:
    - Logical tab order.
    - Visible focus states.
  - Use ARIA roles and labels for non-standard components.
  - Provide sufficient color contrast for text and key UI cues.
- **Screen reader considerations**

  - Ensure meaningful element names, roles, and states.
  - Avoid conveying critical information by color, position, or animation alone.
  - Use live regions thoughtfully; avoid flooding assistive tech with frequent updates.
- **Visual disabilities**

  - Support zoom and dynamic text resizing.
  - Provide option for high-contrast themes.
  - Avoid small tap targets and tightly packed controls.
- **AI-specific: Chat and streaming**

  - Treat each message as a discrete, labeled item (for example, `User`, `Assistant`).
  - For streaming output:
    - Aggregate updates into a single announced message when finished, or
    - Use low-verbosity announcements that do not overwhelm.
  - Provide a way to stop streaming and read at the user’s own pace.
- **AI-specific: Multimodal outputs**

  - For charts, images, or audio generated by AI:
    - Provide textual descriptions or summaries.
    - Ensure controls for playback, pausing, and volume are keyboard-accessible.
    - Label generated media as such.

---

## Content & Microcopy

- **Tone**

  - Clear, respectful, and neutral; avoid slang or sarcasm.
  - Avoid blame; focus on tasks and solutions.
- **Headings and labels**

  - Use descriptive headings; avoid cute or ambiguous titles.
  - Put the most distinctive word early in the label or heading.
- **Instructions**

  - Tell users what to do, not how the system is implemented.
  - Avoid path-dependent phrases such as `Return to the previous screen`; use explicit destination names instead.
- **AI-specific: Prompts and affordances**

  - Replace generic `Ask me anything` with 2–3 domain-specific examples.
  - Offer prompt templates and chips for common tasks.
  - Provide brief guidance on how to get better results (for example, `Specify audience, format, and length`).
- **AI-specific: Disclaimers and limitations**

  - For safety-sensitive areas, include a concise, persistent note that:
    - The AI may be incorrect or incomplete.
    - Users should verify critical information with reliable sources or professionals.
  - Avoid overusing heavy disclaimers so they do not become invisible.
- **AI-specific: Guardrail responses**

  - When declining a request for policy reasons:
    - Clearly state that the system cannot help with that specific request.
    - Offer safe, constructive alternatives where possible.
    - Maintain a respectful tone.

---

## Motion

- **General**

  - Use motion to communicate state changes and spatial relationships, not decoration.
  - Keep animations short and subtle; avoid constant motion.
  - Provide accessibility settings to reduce or disable motion.
- **Loading and progress**

  - Use spinners for brief waits and progress bars for longer tasks.
  - For skeleton screens, match the structure of eventual content to avoid layout shifts.
- **AI-specific: Streaming and transitions**

  - Use gentle streaming animations for AI responses; avoid flashy effects.
  - Ensure streaming text remains readable and selectable.
  - Allow users to pause or stop streaming.

---

## Checklists

### Design Review Checklist (General)

- [ ] Users, tasks, and context are clearly defined.
- [ ] Layout follows a clear hierarchy with adequate white space and grouping.
- [ ] Typography is readable with sufficient hierarchy and line length.
- [ ] Color usage is restrained, consistent, and accessible.
- [ ] Components have clear labels and predictable behavior.
- [ ] Navigation is consistent and supports safe backtracking.
- [ ] Forms clearly distinguish required fields and validate gracefully.
- [ ] Error messages are clear, constructive, and actionable.
- [ ] Accessibility basics are covered: keyboard, screen reader, contrast, scalable text.

### AI-Specific Checklist

- [ ] AI-generated content is visually distinguishable when needed.
- [ ] States are clear: idle, thinking, queued, generating, completed, and error.
- [ ] Uncertainty and limitations are communicated in a non-alarmist way.
- [ ] Users can:
  - [ ] Edit prompts and context easily.
  - [ ] Retry or refine responses.
  - [ ] Revert AI edits to their content.
- [ ] Context in use (files, datasets, settings) is visible and adjustable.
- [ ] Each AI response provides useful quick actions (for example, `Regenerate`, `Refine`, `Copy`).
- [ ] Error handling covers:
  - [ ] Infrastructure issues (timeouts, rate limits).
  - [ ] Content issues (hallucinations, unsafe suggestions).
- [ ] Chat and streaming experiences are accessible with keyboard and assistive tech.
- [ ] AI prompts, examples, and disclaimers are tailored to the product’s domain.

---

## Anti-Patterns

Avoid these patterns:

- Ambiguous icons or unlabeled controls.
- Overloaded screens with too many elements or competing focal points.
- Excessive typefaces, intense colors, or constant animations.
- Modal dialogs that interrupt simple validation or informational flows.
- Hidden or non-obvious critical actions (for example, destructive actions in neutral styling).
- Generic `Ask me anything` without guidance in a domain-specific product.
- AI silently overwriting user content without visibility or reversibility.
- AI answers presented with unjustified certainty in safety-sensitive domains.
- Disabling navigation or escape routes while AI is generating.

---

## Examples (Conceptual Patterns)

- **AI chat workspace**

  - Layout:
    - Left: context panel listing current project, attached files, and presets.
    - Center: chat stream with clear user and assistant messages.
    - Bottom: prompt input with example chips (`Summarize`, `Explain`, `Outline`).
    - Right: sources and settings.
  - Each assistant message:
    - Displays content in structured, scannable form.
    - Shows `Regenerate`, `Refine`, `Copy`.
    - Offers `Show sources` when available.
- **AI-assisted editor**

  - Document body in the center.
  - Side panel listing AI suggestions (`Shorten`, `Improve clarity`, `Change tone`).
  - When applying an edit:
    - Show diff mode (original vs revised).
    - Allow `Accept`, `Reject`, or `Apply partially`.
    - Provide a `Reset to original` action.
- **AI-powered form helper**

  - Standard form layout with clearly labeled fields and groups.
  - `Let AI draft` button near large text areas (for example, description).
  - AI suggestions appear as a preview:
    - `Insert suggestion` button to accept.
    - Edits become user-owned afterward.

---

## References

- Wilbert O. Galitz, *The Essential Guide to User Interface Design: An Introduction to GUI Design Principles and Techniques*, 3rd edition.
- This cheat-sheet extends the book’s general UI principles with AI-first interaction patterns for conversational, generative, and assistive systems.
