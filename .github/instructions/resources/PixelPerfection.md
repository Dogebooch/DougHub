# Pixel Perfect Precision → Machine-Usable UI/UX & Production Guidelines

Source: Pixel Perfect Precision v3, ustwo.:contentReference[oaicite:1]{index=1}

---

# Core Principles

- **Design for users first**

  - Understand what users are trying to do; structure the UI to let them complete tasks quickly. :contentReference[oaicite:2]{index=2}
  - Match visual style to audience: flat, typographic interfaces may suit younger / tech-savvy users; add friendlier, skeuomorphic cues for less tech-savvy groups. :contentReference[oaicite:3]{index=3}
- **Respect environment**

  - Consider viewing distance, lighting, and input device (remote vs touch vs mouse). TV UIs differ radically from mobile (larger text, higher contrast). :contentReference[oaicite:4]{index=4}
- **Accessibility = quality**

  - Accessibility is for *everyone*, not a special mode. Build ease of use, clarity, and inclusive patterns from the start. :contentReference[oaicite:5]{index=5}
- **Design for real data (worst case)**

  - Test with long text, translations, missing images, and varied content, not only “pretty” examples. :contentReference[oaicite:6]{index=6}
- **Use clear affordance**

  - Visual cues (depth, shape, placement, overflowed text) should suggest what’s clickable, scrollable, or draggable. :contentReference[oaicite:7]{index=7}
- **Copy is part of design**

  - Tone and wording should be human, friendly, and explanatory—not bureaucratic. :contentReference[oaicite:8]{index=8}
- **Visual hierarchy**

  - Use size, contrast, and weight to guide reading order; start from what you want users to see first. Western users tend to start top-left. :contentReference[oaicite:9]{index=9}
- **Test & prototype**

  - Test on real devices, not just in the design tool. Use low-effort prototypes (paper → simple builds) to explore interactions before polishing. :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11}
- **Be realistic in dev**

  - Perfect visual fidelity is less important than stability and usability; don’t fight for pixel-perfect matches if it blocks bug fixes or improvements. :contentReference[oaicite:12]{index=12}

---

# Layout

## Sharpness & Alignment

- All straight edges must sit **on pixel**—no blurred edges. :contentReference[oaicite:13]{index=13}
- Maintain consistent margins, gutters, and spacing between similar elements across screens (titles, nav bars, footers). Use a **grid** as the backbone. :contentReference[oaicite:14]{index=14}

**Do**

- Align objects to a shared grid.
- Reuse the same margin/spacing tokens per breakpoint.

**Avoid**

- Sub-pixel positions that cause soft edges.
- Elements “jumping” between screens due to inconsistent layout.

## Content Structure & Navigation Layout

- Put **most important information closest to where users land**; use progressive disclosure for detail. :contentReference[oaicite:15]{index=15} :contentReference[oaicite:16]{index=16}
- Keep navigation elements (back, menu, search, tabs) in **consistent positions** with consistent styles and labels across screens. :contentReference[oaicite:17]{index=17} :contentReference[oaicite:18]{index=18}
- Prefer **scrolling within a page** over many micro-pages; scrolling is easier than jumping between multiple screens, but don’t make pages endlessly long. :contentReference[oaicite:19]{index=19}
- Limit scrolling to **one direction** (vertical OR horizontal) on a given screen to reduce cognitive and physical effort. :contentReference[oaicite:20]{index=20}

## Steps & Flow Depth

- Aim to keep related information reachable within **≤ 4 screens**; more creates friction. :contentReference[oaicite:21]{index=21}
- Avoid needless intermediate “info → info → info → finally destination” steps; compress where possible.

## Grouping & Titles

- Every major screen needs a **clear, descriptive title** indicating where the user is and what the content is. :contentReference[oaicite:22]{index=22}
- Use **section breaks** and headings to chunk content into meaningful blocks.

---

# Typography

## Basics

- Treat type as a first-class design element; most information is text. :contentReference[oaicite:23]{index=23}
- **Minimum size:** 12pt; comfortable reading around **16pt (1em)**. Smaller text causes strain, especially on low-density screens. :contentReference[oaicite:24]{index=24}

## Line Length & Spacing

- Keep lines **≤ ~80 characters**; target 45–75 characters, with 66 chars as a sweet spot (including spaces). :contentReference[oaicite:25]{index=25}
- Set line spacing (leading) to about **1.5× font size**; paragraph spacing ≈ **1.5× line spacing** for clear separation. :contentReference[oaicite:26]{index=26}
- Break long text into paragraphs of **≈5 lines max** to aid scanning. :contentReference[oaicite:27]{index=27}

## Alignment & Formatting

- Multi-line text should be **left-aligned**. Avoid center-aligned or fully-justified body text due to inconsistent word spacing and “rivers”. :contentReference[oaicite:28]{index=28}
- Keep formatting simple:
  - Prefer sans-serif for legibility.
  - Avoid long blocks of **all caps**, underlining, or italics. Screen readers and dyslexic/visually-impaired users benefit from clean shapes. :contentReference[oaicite:29]{index=29}
- Disable automatic **hyphenation**; many devices don’t support it and it hurts fidelity. :contentReference[oaicite:30]{index=30}

## Text Containers & Alignment to Objects

- Use **paragraph text containers** for multi-line content; avoid manual line breaks (point text) which break when copy changes. :contentReference[oaicite:31]{index=31}
- Convert point ↔ paragraph text via `Type > Convert to Paragraph/Point Text` as needed. :contentReference[oaicite:32]{index=32}
- When vertically centering text inside shapes:
  - Align using **x-height** rather than cap height for mixed-case text.
  - For all caps or numbers, align on **cap height**. :contentReference[oaicite:33]{index=33} :contentReference[oaicite:34]{index=34}

## Don’t Merge Text into Graphics

- Keep text separate from bitmaps wherever possible:
  - Enables text-to-speech, user scaling, and theming.
  - Avoids having to re-export graphics for copy tweaks. :contentReference[oaicite:35]{index=35}

---

# Color

## Palette Construction

- Prefer **HSB (Hue–Saturation–Brightness)** when building palettes; keep Hue constant and adjust S/B for tints and shades—numbers map more intuitively than RGB. :contentReference[oaicite:36]{index=36}

## Colour Management (Digital)

- For screen products, avoid complex CM workflows:
  - In Photoshop: set Working RGB to **Monitor RGB – Display** and color management RGB policy to **Off**. :contentReference[oaicite:37]{index=37}
  - In Save for Web: **disable** Convert to sRGB; set preview to **Monitor Color**. :contentReference[oaicite:38]{index=38}
- Avoid using color profiles on exported assets; they can mismatch with code-rendered colors. :contentReference[oaicite:39]{index=39}

## Color & Meaning

- Respect established color+shape conventions:
  - Green + tick ⇒ success/OK.
  - Red + cross ⇒ error/bad.
  - Yellow + triangle ⇒ warning.
  - Blue + circle ⇒ information. :contentReference[oaicite:40]{index=40}

## Contrast & Color-Blindness

- Provide good contrast between foreground and background, especially for text and key icons. :contentReference[oaicite:41]{index=41}
- Don’t rely on color alone. Always pair color with:
  - icons, patterns, labels, position, or shape. :contentReference[oaicite:42]{index=42}
- For charts/graphs, differentiate series with **patterns** or additional encodings, not just hue. :contentReference[oaicite:43]{index=43}
- Use contrast checking tools (e.g., Colour Contrast Analyser, Snook’s checker) and aim for at least **WCAG AA** contrast; AAA is ideal but may look harsh if overdone. :contentReference[oaicite:44]{index=44}

## Simulation & Special Systems

- Use built-in proof setups (Photoshop `View > Proof Setup > Color Blindness`) or a system-wide tool like **Sim Daltonism** to preview palettes under color-blind conditions. :contentReference[oaicite:45]{index=45} :contentReference[oaicite:46]{index=46}
- For non-textual color cues, consider symbol systems like **ColorADD** (triangles, lines, and overlays representing hues and light/dark variations). :contentReference[oaicite:47]{index=47}

---

# Components

## Buttons vs Links

- Use **buttons for actions**, not plain text links. Links suggest navigation, not “do something”. :contentReference[oaicite:48]{index=48}
- Never underline non-clickable text; underlines visually signal links. :contentReference[oaicite:49]{index=49}

## States

- Define and design all states up front:
  - default, hover (if applicable), active/pressed, selected, disabled.
- Export all states at **identical dimensions** so they swap cleanly in code. :contentReference[oaicite:50]{index=50} :contentReference[oaicite:51]{index=51}

## Borders & Corner Radii

- For a shape with border:
  - Best rule: **outer radius = inner radius + border width**. This keeps border thickness visually consistent at corners. :contentReference[oaicite:52]{index=52}
- When starting from outer radius and subtracting border width yields sharp inner corners, add a small inner radius (“fillet”) for nicer appearance, even if mathematically imperfect. :contentReference[oaicite:53]{index=53}

## Triangles & Icons

- For equilateral triangles drawn from a square base:
  - Scale height to **86.6%** of width (shortest edge at bottom). :contentReference[oaicite:54]{index=54}

---

# Interaction Patterns

## Touch Targets

- Minimum **touch area**: ~7mm × 7mm for finger contact; leave ≥2mm gap between touch targets to avoid accidental taps. Wider targets for thumbs (≈25mm width). :contentReference[oaicite:55]{index=55}

## Error Prevention

- Place risky actions further away / less prominent; provide extra confirmations or “guard rails.” :contentReference[oaicite:56]{index=56}
- Use **checked data** patterns (inline validation) so users know whether their input is valid as they type. :contentReference[oaicite:57]{index=57}
- Prefer **choice controls** (radio, select, segmented control) over free text when possible to reduce errors. :contentReference[oaicite:58]{index=58}
- For multi-step operations (e.g., checkout):
  - Present **review screen** summarising choices with ability to go back and edit before final submission. :contentReference[oaicite:59]{index=59}
- Any destructive or hazardous action should be **reversible** (trash folder, version history) when feasible. :contentReference[oaicite:60]{index=60}

## Feedback

- Always acknowledge user actions:
  - Button press states, loading spinners, in-context messages (“Saving… / Saved”). :contentReference[oaicite:61]{index=61}
- Provide **multi-sensory feedback** (visual + sound / haptic) so users in noisy or silent environments still perceive it. :contentReference[oaicite:62]{index=62}
- Error messages:
  - Human-readable explanation.
  - Guidance on what to do next.
  - Short-circuit path back to a safe/previous screen. :contentReference[oaicite:63]{index=63}

---

# Navigation

- Keep nav **consistent:** same positions, patterns, and labels across screens. :contentReference[oaicite:64]{index=64}
- Minimise steps (≤4 pages to access any key item where possible). :contentReference[oaicite:65]{index=65}
- Use **titles** and clear section headings to locate users. :contentReference[oaicite:66]{index=66}
- Keep scroll direction **one-dimensional**, and prefer scroll over paging for continuous content. :contentReference[oaicite:67]{index=67}
- For long lists, use **numbered lists** when >3–4 items; numbers improve navigation and referencing compared to bullets. :contentReference[oaicite:68]{index=68}

---

# States & Feedback (Forms & Fields)

- Place error messages **next to the relevant field**, not at the top of the page. :contentReference[oaicite:69]{index=69}
- Give immediate validation (green checks, helpful inline hints) where appropriate, rather than only on submit. :contentReference[oaicite:70]{index=70}

---

# Forms & Validation

- Place **labels above fields**, not inside as placeholder text:
  - Screen readers then read “Name, Gyppsy, enter here” instead of just the value.
  - Users still see the label after typing. :contentReference[oaicite:71]{index=71}
- Use clear field order and grouping; mirror natural workflows.
- Provide **defaults** instead of free text where possible (e.g., dropdown for colour instead of free text input). :contentReference[oaicite:72]{index=72}
- Give users a **review step** with ability to go back and correct. :contentReference[oaicite:73]{index=73}

---

# Error Handling & Copy

## Dialog & CTA Wording

- Copy must be unambiguous. Example bad pattern:

  > “Do you wish to cancel this order?
  > [Cancel] [Yes]”
  >

  It’s unclear what “Cancel” cancels. Instead:

  > “Do you wish to cancel this order?
  > [No] [Cancel order]” :contentReference[oaicite:74]{index=74}
  >
- Always specify **what will happen** if each button is pressed.

## Text Structure

- Break large blocks of text into smaller paragraphs or lists; consider diagrams where sequencing matters. :contentReference[oaicite:75]{index=75} :contentReference[oaicite:76]{index=76}
- Use lists and simple diagrams for users with cognitive or organisational difficulties. :contentReference[oaicite:77]{index=77}

## Abbreviations & Links

- Introduce abbreviations with expansion on first use; avoid unnecessary acronyms. :contentReference[oaicite:78]{index=78}
- Replace “Click here” with **descriptive link text** that makes sense on its own, and include extra details like file size for downloads. :contentReference[oaicite:79]{index=79}

---

# Accessibility

## Multi-sensory Design

- Don’t rely on a single sense (vision, hearing, touch) for critical information; provide **multiple channels** (text, icon, sound, vibration). :contentReference[oaicite:80]{index=80}

## Clarity & Progression

- Keep content context-relevant and concise. Use progressive disclosure to prevent overload. :contentReference[oaicite:81]{index=81}
- Keep assets lightweight for mobile or low-bandwidth environments. :contentReference[oaicite:82]{index=82}

## Movement & Flashing

- Avoid flashing content at >3 flashes per second; this can trigger seizures for photosensitive users. :contentReference[oaicite:83]{index=83}
- Avoid auto-starting tickers and marquees; if movement is necessary:
  - Provide play/pause control.
  - Don’t make it the only way to obtain the information. :contentReference[oaicite:84]{index=84}

## Testing Accessibility

- Test real devices using platform accessibility features (black & white mode, zoom, text-to-speech). Include participants who rely on these features. :contentReference[oaicite:85]{index=85}

---

# Motion

- Use subtle animations to:
  - Draw attention to new things (e.g., bouncing button).
  - Clarify interactions (transitions between states). :contentReference[oaicite:86]{index=86}
- Avoid motion that:
  - Loops constantly without purpose.
  - Interferes with reading or understanding.
  - Can’t be paused or stopped by the user. :contentReference[oaicite:87]{index=87}

---

# Production & Tooling (Photoshop)

## Setup: Colour & Profiles

- System:
  - `System Preferences > Displays > Color` set to current device profile (e.g., Color LCD). :contentReference[oaicite:88]{index=88}
- Photoshop:
  - `Edit > Color Settings…` →
    - Working RGB: **Monitor RGB – Display**
    - Color Management Policy RGB: **Off** :contentReference[oaicite:89]{index=89}
  - Save for Web:
    - **Uncheck** Convert to sRGB.
    - Preview: **Monitor Color**. :contentReference[oaicite:90]{index=90}

## Pixel Precision

- Prefer **Shape Layers** for UI elements:
  - Editable, scalable, smaller files than Smart Objects/bitmaps.
  - Use vector masks where possible for flexibility. :contentReference[oaicite:91]{index=91} :contentReference[oaicite:92]{index=92}
- Enable **Snap Vector Tools and Transforms to Pixel Grid**; consider an Action + shortcut to toggle this on/off for sub-pixel work. :contentReference[oaicite:93]{index=93}
- Turn on `View > Snap` and configure Snap To for guides, layers, and document bounds. :contentReference[oaicite:94]{index=94}
- Use grids:
  - 10px gridlines with 10 subdivisions is a good balance of precision vs noise. :contentReference[oaicite:95]{index=95}
- Use tools like **GuideGuide** to automate guide creation for consistent spacing systems. :contentReference[oaicite:96]{index=96}

## Text & Paragraph Handling

- Align paragraphs using correct alignment options; don’t fake alignment by manually spacing them. :contentReference[oaicite:97]{index=97}
- Use paragraph text for multi-line copy; convert point → paragraph as needed. :contentReference[oaicite:98]{index=98}
- Increase default leading slightly beyond “Auto” for readability; example: 20pt leading instead of default for certain sizes. :contentReference[oaicite:99]{index=99}

## Techniques & Organisation

- For complex vectors:
  - Draw in Illustrator, **outline strokes**, then paste as Shape Layer or Smart Object. :contentReference[oaicite:100]{index=100}
- Be cautious with blending modes on assets that will be exported separately; if they require underlying layers to work, recreate them as independent effects. :contentReference[oaicite:101]{index=101}
- Clean files:
  - Delete empty layers (`File > Scripts > Delete All Empty Layers`). :contentReference[oaicite:102]{index=102}
  - Remove unused layer styles with a dedicated script/extension. :contentReference[oaicite:103]{index=103}
  - Unlock layers before handing off to avoid blocked edits. :contentReference[oaicite:104]{index=104}
  - Use **Layer Comps** to store different states/variations in a single PSD. :contentReference[oaicite:105]{index=105}

## Export

- Prefer **PNG** for UI assets; keep them uncompressed since dev environments apply their own compression. :contentReference[oaicite:106]{index=106}
- Use **Photoshop Generator** (File > Generate) to auto-export layers/groups named with file extensions; supports scaling and multiple variants. :contentReference[oaicite:107]{index=107}
- If no Generator, use ustwo **Crop & Export** scripts:
  - Prepare: each asset in its own top-level layer/group, properly named. :contentReference[oaicite:108]{index=108}
  - Scripts export each as PNG using naming templates (`[filename][layername]`, etc.). :contentReference[oaicite:109]{index=109}
- Always use **Save for Web**, not Save As, for assets—file sizes are significantly smaller. :contentReference[oaicite:110]{index=110}
- If transparency not needed, convert PNG24 → **PNG8** to halve file size (when quality is unchanged). :contentReference[oaicite:111]{index=111}
- Optionally run assets through **ImageOptim** (except iOS-specific constraints) to strip metadata and compress further. :contentReference[oaicite:112]{index=112}
- For low-bit-depth devices, convert gradients to **565** (16-bit) with dithering (Ximagic ColorDither) and automate batch processing with Actions+Batch. :contentReference[oaicite:113]{index=113} :contentReference[oaicite:114]{index=114}

---

# Production & Tooling (Illustrator)

- Color settings: match Photoshop (`Edit > Color Settings…` → RGB = Monitor RGB – Display, policies Off). :contentReference[oaicite:115]{index=115}
- Preferences:
  - Keyboard increment: **1px** for precise nudging.
  - Units (General + Stroke): **Pixels** (leave Type in Points). :contentReference[oaicite:116]{index=116}
- Grid: 10px gridlines with 10 subdivisions. :contentReference[oaicite:117]{index=117}
- Snap to Grid: enable for pixel-aligned layouts. :contentReference[oaicite:118]{index=118}
- Smart Guides: use when you need snapping to geometric constructs (e.g., intersection of shapes at 45°). :contentReference[oaicite:119]{index=119}
- Transform panel:
  - Use it to check exact pixel dimensions/positions for shapes or points.
  - Use width/height link to scale proportionally. :contentReference[oaicite:120]{index=120}
- Turn off **Align New Objects to Pixel Grid** (super-villain!):
  - It can unexpectedly move objects when you add strokes. :contentReference[oaicite:121]{index=121}
- Beware `View > Pixel Preview`; it may *look* pixel-perfect while underlying vectors are not. :contentReference[oaicite:122]{index=122}
- Organise shapes into sensible groups instead of scattering them over a massive canvas. :contentReference[oaicite:123]{index=123}

---

# Organisation & Delivery

## Naming & Versioning

- Use a clear, consistent naming system for assets:
  - e.g., `btn_home_play_blue_default`, `icn_global_signal_full` or CamelCase `BtnHomeNewDefault`. :contentReference[oaicite:124]{index=124}
- Use structured versioning:
  - `Screen.psd` at top level for the latest.
  - Archive copies as `Screen_YYMMDD_rNN.psd`. :contentReference[oaicite:125]{index=125}

## Deliverables

- Don’t send massive specs listing every measurement; developers prefer:
  - Flows and interaction diagrams.
  - Prototypes.
  - Short motion reference clips. :contentReference[oaicite:126]{index=126}
- Keep a **style guide** file as the source of truth for:
  - Type styles.
  - Colors.
  - Spacing.
  - Component states. :contentReference[oaicite:127]{index=127}
- Before handoff, verify:
  - All assets exported.
  - All object states defined.
  - Style guide present.
  - Key flows clarified.
  - Then… **check again.** :contentReference[oaicite:128]{index=128}

---

# Checklists

## Screen-Level UI Checklist

- [ ] All edges and icons are pixel-sharp.
- [ ] Layout uses a consistent grid & spacing system.
- [ ] Titles clearly indicate where the user is.
- [ ] Navigation elements are consistent across screens.
- [ ] Primary actions use buttons (not plain links) with full state set.
- [ ] Touch targets meet minimum 7mm × 7mm and have gaps.

## Typography & Copy Checklist

- [ ] Base body size ≥12pt; target ~16pt for reading.
- [ ] Lines 45–75 chars; line spacing ≈1.5× font size.
- [ ] Left-aligned paragraphs; no justified body text.
- [ ] No all-caps paragraphs, unnecessary italics, or underlines.
- [ ] Long text broken into paragraphs/lists; diagrams used if helpful.
- [ ] Links are descriptive (“Download Pixel Perfect Precision Handbook (25MB)”), not “Click here”.

## Accessibility Checklist

- [ ] UI does not rely on color alone to convey state.
- [ ] Sufficient text/background contrast (AA+).
- [ ] No flashing > 3 times/sec; motion is user-controllable where needed.
- [ ] Works with text-to-speech; labels aren’t only placeholders.
- [ ] Error messages sit next to fields and explain recovery.
- [ ] Tested with platform accessibility features on real devices.

## Production & Handoff Checklist

- [ ] Photoshop and Illustrator color settings configured (Monitor RGB, policies Off).
- [ ] Grids + snapping enabled; shape layers used for UI components.
- [ ] All assets exported via Generator/scripts using naming convention.
- [ ] PNG8 used where transparency isn’t needed; heavy assets optimised.
- [ ] Files are clean: no empty layers, stray FX, or locked surprises.
- [ ] Style guide file updated and shared with devs.
- [ ] Version history stored in archive with dated filenames.

---

# Anti-Patterns (Naughty)

- Overloading screens with content and tiny fonts.
- Using inconsistent colors/shapes for success and error.
- Using hyperlinks instead of buttons for actions.
- Embedding all text into images.
- Center/justified body copy, long all-caps blocks.
- Navigation labels and positions changing between screens.
- Designing only for “ideal” content, not real-world long or missing data.
- Failing to provide feedback for loading or button presses.
- Overusing flashing/moving text and auto-playing tickers.
- Ad-hoc asset naming and “Screen_FINAL_FINAL3.psd” chaos. :contentReference[oaicite:129]{index=129}

---

# Examples

## Example: Button Asset Naming & States

```text
btn_home_play_blue_default.png
btn_home_play_blue_pressed.png
btn_home_play_blue_disabled.png
```
