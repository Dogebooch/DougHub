
# Principles of Product Design → Machine-Usable Guidelines

Source: *Principles of Product Design* (DesignBetter.co, Aaron Walter). :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

Book structure (for mapping):

- Guess less / Stop wasting time
- Story First / Find your North Star
- Pencils before pixels / Think divergently
- Show and tell / Create a culture of feedback
- Fast feedback / Product prototyping—accelerated
- Lateral design / We’re better together
- Break the black box / Product design is people :contentReference[oaicite:2]{index=2}

---

# Core Principles

## P1 — Guess Less (Evidence Over Opinion)

**Goal:** Reduce waste by grounding decisions in real customer insight instead of internal guesses.

- Treat guessing as an anti-pattern: it’s expensive, uncompetitive, and arrogant. :contentReference[oaicite:3]{index=3}
- Make customer research a default part of design, not a special event. :contentReference[oaicite:4]{index=4}
- Combine **quantitative** (what/when/how often) with **qualitative** (why/how it feels). Never rely on one alone. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}
- Use existing data first: analytics, surveys, NPS, support tickets, sales data, customer database, and session recordings. :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}
- Make research continuous with:
  - Automated surveys (NPS, post-signup, account-closing, topic-specific micro-surveys). :contentReference[oaicite:9]{index=9} :contentReference[oaicite:10]{index=10}
  - Background data tools (e.g., session recording, in-app messaging, tech-stack detection). :contentReference[oaicite:11]{index=11} :contentReference[oaicite:12]{index=12}
- Talk to customers regularly; schedule interviews monthly even outside specific projects. :contentReference[oaicite:13]{index=13}

**Example – Minimal research pipeline for a feature:**

1. Pull usage analytics for relevant flows (drop-offs, error rates, frequency).
2. Send a short ad-hoc survey to a targeted segment. :contentReference[oaicite:14]{index=14}
3. Use survey responses to recruit 5–10 interview participants with diverse traits. :contentReference[oaicite:15]{index=15}
4. Run interviews and extract 1–2 key insights per participant. :contentReference[oaicite:16]{index=16}
5. Summarize into personas + job stories (see below), then design.

---

## P2 — Story First / Find Your North Star

**Goal:** Use narrative to align teams on how the product fits into customers’ lives.

- Create a **clear, compelling product story** before detailed design. :contentReference[oaicite:17]{index=17}
- Use story to define the **North Star**—a vivid picture of the future product impact that guides decisions. :contentReference[oaicite:18]{index=18}
- Use stories especially for:
  - New products
  - Long / multi-team projects
  - Cross-channel experiences (web + mobile + offline) :contentReference[oaicite:19]{index=19}

### Story Artifacts

- **Product story video** (low-fi is fine)

  - Focus on people, context, and value; *not* final UI visuals. :contentReference[oaicite:20]{index=20}
  - Use colleagues as actors, simple editing, speech bubbles instead of full dialogue to ship faster. :contentReference[oaicite:21]{index=21}
- **Personas** (segment-level “who”)

  - Based on interviews; represent common traits and goals in key customer segments. :contentReference[oaicite:22]{index=22}
  - Keep them **visible** (posters, boards) so everyone remembers who they serve. :contentReference[oaicite:23]{index=23}
  - Refresh regularly; treat as snapshots, not permanent truth. :contentReference[oaicite:24]{index=24}
- **Job stories** (situation-level “why”)

  - Derived from real interviews; never invented in a vacuum. :contentReference[oaicite:25]{index=25}
  - Use the structure:
    > **When** \<situation\> **I want to** \<motivation\> **so I can** \<expected outcome\>. :contentReference[oaicite:26]{index=26}
    >
  - Example from the book:
    > When I commute to and from work for hours each day in my car
    > I want to do something productive and stimulating
    > so I can feel like I’m not wasting time and actually make my commute productive. :contentReference[oaicite:27]{index=27}
    >

**Usage pattern:**

- Before implementing a feature, write:
  - 1–3 job stories
  - A short storyboard or journey (steps in the story)
- Use these to:
  - Prioritize features: “Does this step support the story?”
  - Keep teams aligned over long timelines.

---

## P3 — Pencils Before Pixels / Think Divergently

**Goal:** Explore many options cheaply before committing to one polished solution.

- Start with **low-fidelity** exploration (paper, whiteboard), not polished UI. :contentReference[oaicite:28]{index=28}
- Generate **many** crude options first; only later invest in pixel-perfect design. :contentReference[oaicite:29]{index=29}
- Use sketching because it’s fast, fluid, and disposable. :contentReference[oaicite:30]{index=30} :contentReference[oaicite:31]{index=31}

**Divergent sketching pattern (team):**

1. Clarify constraints and goals (problem, users, success metrics).
2. Everyone sketches individually for a fixed time (e.g., 10–20 min).
3. Post all sketches on a wall or shared board.
4. Walk the wall, ask clarifying questions, and dot-vote on promising ideas.
5. Combine and refine into 1–2 stronger directions.

**Anti-pattern:** Jumping straight into hi-fi tools leads to precious designs that are hard to discard and prematurely narrow exploration. :contentReference[oaicite:32]{index=32}

---

## P4 — Show & Tell / Culture of Feedback

**Goal:** Make feedback a default, safe part of design work.

- Healthy design teams show work early and often; feedback is visible in the environment (walls, boards, shared tools). :contentReference[oaicite:33]{index=33} :contentReference[oaicite:34]{index=34}
- Build **psychological safety**: it must feel safe to take risks, be vulnerable, and show in-progress work. :contentReference[oaicite:35]{index=35}
- Always critique **the work, not the person**. Use “the design” instead of “you”. :contentReference[oaicite:36]{index=36}
- Encourage specific, goal-referencing feedback instead of vague likes/dislikes. :contentReference[oaicite:37]{index=37}

**Design review pattern (in-person or remote):** :contentReference[oaicite:38]{index=38} :contentReference[oaicite:39]{index=39}

1. **Set context:** facilitator reminds everyone of goals and constraints.
2. **Designer frames the problem** and clearly states what feedback they need (e.g., “Is this upload workflow intuitive?”).
3. Silent review: everyone studies the work quietly first. :contentReference[oaicite:40]{index=40}
4. Group feedback:
   - Speak to goals (“This design doesn’t meet the goal of X because…”), not taste.
   - Avoid solution pitching until problems are clear.
5. Designer mostly listens; no pitching or over-explaining. :contentReference[oaicite:41]{index=41}
6. Facilitator summarizes outcomes and next steps.

---

## P5 — Fast Feedback / Product Prototyping

**Goal:** Test realistic experiences early, learn quickly, and adjust before development.

- Build **high-fidelity prototypes** before writing production code; teams that test early learn faster and have advantage. :contentReference[oaicite:42]{index=42}
- A good prototype:
  - Feels real enough that customers don’t notice it’s fake. :contentReference[oaicite:43]{index=43}
  - Is quick to build and easy to change. :contentReference[oaicite:44]{index=44}
- Prototype only the **riskiest or most uncertain parts**, not the entire app. :contentReference[oaicite:45]{index=45}
- Use modern tools (e.g., Sketch/Figma + prototyping, Keynote, etc.) to avoid hand-coding prototypes. :contentReference[oaicite:46]{index=46} :contentReference[oaicite:47]{index=47}

**Design system + pattern library:**

- Maintain a reusable library of standard UI components (“LEGO blocks”) to accelerate prototyping and ensure consistency. :contentReference[oaicite:48]{index=48}
- Investing in a pattern library reduces time spent “noodling” on visuals and frees time to align product with real needs. :contentReference[oaicite:49]{index=49}

**Testing loop:**

1. **Internal testing:** share prototypes with teammates (design, engineering, others) for fresh eyes and quick fixes. :contentReference[oaicite:50]{index=50}
2. **Customer testing:**
   - Use simple script: welcome → icebreaker → intro to prototype → tasks → debrief. :contentReference[oaicite:51]{index=51}
   - Don’t help users during tasks; assistance contaminates feedback. :contentReference[oaicite:52]{index=52}
3. **Remote testing:** use scheduled calls + screen sharing + recording to test with users anywhere. :contentReference[oaicite:53]{index=53} :contentReference[oaicite:54]{index=54}

**Example remote-test workflow (from Vox):** :contentReference[oaicite:55]{index=55}

- Schedule via calendar tool → share prototype link → run remote session with voice + screen → record → review and annotate → share insights in team channel.

---

## P6 — Lateral Design / We’re Better Together

**Goal:** Build cross-functional teams and processes where design, product, and engineering share ownership.

- Organizational design influences product design: mixed, collaborative teams create better products. :contentReference[oaicite:56]{index=56}
- Design values (e.g., Spotify’s “be alive”) help everyone understand why certain design decisions matter. :contentReference[oaicite:57]{index=57}
- Lateral design is compatible with Agile, Lean, etc.; it’s about **respect and empathy across disciplines**. :contentReference[oaicite:58]{index=58}

**Implementation to-do list:** :contentReference[oaicite:59]{index=59}

1. Start small with a **1-week design sprint**.
2. Form a **cross-functional working group** for a project: at minimum design, engineering, and product manager.
3. Evolve into an **EPD structure** where engineering, product, and design share power and report at similar levels (e.g., to CEO/COO).

---

## P7 — Break the Black Box / Product Design Is People

**Goal:** Keep design visible, connected, and influential as the company scales.

- When design becomes invisible, it loses power and risks being misunderstood or ignored. :contentReference[oaicite:60]{index=60} :contentReference[oaicite:61]{index=61}
- Avoid the “grand reveal”; share progress continuously to get honest feedback early. :contentReference[oaicite:62]{index=62}
- Build **social capital** across org:
  - Meet with developers, researchers, PMs, sales, marketing, and support to learn their constraints and insights. :contentReference[oaicite:63]{index=63} :contentReference[oaicite:64]{index=64}
  - Include executives; learn company-level strategy. :contentReference[oaicite:65]{index=65}
- Make design **physically and digitally visible**: walls, project bays, shared channels, and open design reviews. :contentReference[oaicite:66]{index=66} :contentReference[oaicite:67]{index=67}

**Concrete to-do list for breaking the black box:** :contentReference[oaicite:68]{index=68}

- Share early and often: recurring design review days open to anyone.
- Network across the org chart; treat it as a map of potential allies.
- Be open and accessible:
  - Post work in public spaces (walls, Slack channels).
  - Present at informal gatherings (coffee hours, lunch-and-learns).
- Ask for feedback at every stage (without turning it into design-by-committee).

---

# Layout

The book does **not** define visual layout systems (grids, breakpoints, spacing).

**Relevant guidance:**

- Use a **pattern library/design system** to unify layout across products and platforms and speed up prototyping. :contentReference[oaicite:69]{index=69}
- Use consistent patterns so cross-functional teams can focus on solving product problems, not reinventing layout.

---

# Typography

Not discussed in detail.

- Only indirectly: critique language should reference typography in relation to goals (e.g., “type feels trendy, conflicts with trust-building goal”), not taste. :contentReference[oaicite:70]{index=70}

---

# Color

Not addressed as a system; only in context of design values (e.g., “be alive” using imagery and color). :contentReference[oaicite:71]{index=71}

---

# Components

**Design systems and patterns:**

- Create a **pattern library** of reusable components (buttons, forms, cards, flows) to compose new UIs quickly. :contentReference[oaicite:72]{index=72}
- Use pattern libraries to:
  - Maintain consistency across products and platforms. :contentReference[oaicite:73]{index=73}
  - Speed up prototyping and reduce time spent on surface tweaks. :contentReference[oaicite:74]{index=74}
- Refresh library as you test patterns in real prototypes and learn from user feedback.

---

# Interaction Patterns (Team & Process)

The book focuses on **process patterns** rather than specific UI widget interactions.

## Surveys

- Use surveys sparingly; too many alienate customers. :contentReference[oaicite:75]{index=75}
- Before sending:
  - Define clear learning goals. :contentReference[oaicite:76]{index=76}
  - Keep as short as possible; remove “nice-to-know” questions. :contentReference[oaicite:77]{index=77}
  - Don’t ask for data you already have in your systems. :contentReference[oaicite:78]{index=78}
  - End with an open-ended “Anything else you want to tell us?” to catch unexpected insights + interview candidates. :contentReference[oaicite:79]{index=79}

**Types:**

- Automated:
  - NPS
  - Post-signup
  - Post-account-closing
  - Topic-specific micro-surveys (targeted via snippet on key pages). :contentReference[oaicite:80]{index=80} :contentReference[oaicite:81]{index=81}
- Ad-hoc:
  - Deep dives on features or themes
  - Use early questions (e.g., company size, product type) to enable cohort analyses later. :contentReference[oaicite:82]{index=82}

## Customer Interviews

- Use surveys to identify high-value interview candidates (new, churned, extreme opinions, unusual behavior). :contentReference[oaicite:83]{index=83} :contentReference[oaicite:84]{index=84}
- Keep interviews ~20–30 minutes; record audio/video. :contentReference[oaicite:85]{index=85} :contentReference[oaicite:86]{index=86}
- Limit interviewers; assign a dedicated note-taker. :contentReference[oaicite:87]{index=87}
- Watch for energy changes (tone, leaning in, strong words) as signals of important topics. :contentReference[oaicite:88]{index=88}
- Expect 1–2 “golden insights” per session; don’t chase every detail. :contentReference[oaicite:89]{index=89}

## Design Standups

- Daily (or frequent) 5–15 minute check-ins; everyone stands. :contentReference[oaicite:90]{index=90}
- Each person answers:
  1. What did you do yesterday?
  2. What will you do today?
  3. Any impediments? :contentReference[oaicite:91]{index=91}
- Keep standups **strictly about progress**, not impromptu critiques. :contentReference[oaicite:92]{index=92}

## Retrospectives & Postmortems

- After each launch or sprint, run a retrospective:
  - What worked?
  - What didn’t?
  - What will we change? (Start / Stop / Keep). :contentReference[oaicite:93]{index=93}
- Use pre-retro surveys to avoid groupthink and capture quieter perspectives. :contentReference[oaicite:94]{index=94}
- Use **blameless postmortems** for failures to focus on learning, not punishment. :contentReference[oaicite:95]{index=95}

---

# Navigation

Not covered (no specific IA/sitemap/flow rules).
Use this book alongside other IA-focused resources.

---

# States & Feedback (Loops, Not UI States)

**Feedback loops in product & team:**

- Build feedback into the **everyday environment** (walls, tools, conversations) so it happens naturally. :contentReference[oaicite:96]{index=96} :contentReference[oaicite:97]{index=97}
- Shorten the loop from idea → prototype → customer feedback → iteration. :contentReference[oaicite:98]{index=98}
- Use always-on tools (surveys, Intercom-style messaging, session recording) to gather “background learning” without extra effort. :contentReference[oaicite:99]{index=99}

---

# Forms & Validation

Not explicitly addressed in this book.

---

# Error Handling

Not explicitly addressed in this book (focused on process rather than UI error states).

---

# Accessibility

Not covered directly; separate accessibility guidelines needed.

---

# Content & Microcopy

**Language from customers:**

- Use customer interviews to learn the **words and phrases users naturally use**; apply them in UI copy and marketing. :contentReference[oaicite:100]{index=100}
- In critiques, evaluate copy against project goals (“feels trendy vs. trustworthy”), not taste. :contentReference[oaicite:101]{index=101}

---

# Motion

- Motion is mentioned only tangentially (e.g., Keynote prototypes, design values like “be alive”).
- Use motion to **clarify flows and make interfaces feel alive**, but the book doesn’t provide specific timing or easing rules. :contentReference[oaicite:102]{index=102} :contentReference[oaicite:103]{index=103}

---

# Checklists

## Research & “Guess Less” Checklist

- [ ] For each new feature/project, identify:
  - [ ] Existing analytics and cohorts
  - [ ] Existing surveys/NPS/CSAT data
  - [ ] Existing qualitative insights (support, sales, research) :contentReference[oaicite:104]{index=104}
- [ ] Define 1–3 research questions (not just methods).
- [ ] Configure or update:
  - [ ] Automated surveys (NPS, post-signup, post-exit)
  - [ ] Micro-surveys on critical flows
  - [ ] Session recording on key paths :contentReference[oaicite:105]{index=105} :contentReference[oaicite:106]{index=106}
- [ ] Run at least one targeted ad-hoc survey if needed. :contentReference[oaicite:107]{index=107}
- [ ] Recruit interviewees from survey responses and key cohorts. :contentReference[oaicite:108]{index=108}
- [ ] Conduct and synthesize interviews (1–2 insights each). :contentReference[oaicite:109]{index=109}

## Story & Alignment Checklist

- [ ] Write or update:
  - [ ] Product story
  - [ ] Storyboard / user journey
  - [ ] 1+ personas
  - [ ] 1+ job stories (When / I want / so I can). :contentReference[oaicite:110]{index=110}
- [ ] Share story artifacts in visible locations and team spaces. :contentReference[oaicite:111]{index=111}
- [ ] Use story as acceptance criteria for feature proposals.

## Exploration & Prototyping Checklist

- [ ] Run at least one divergence session (sketching) before hi-fi design. :contentReference[oaicite:112]{index=112}
- [ ] Generate multiple options; avoid 1-concept meetings.
- [ ] Choose a small set of flows to prototype (riskiest/uncertain). :contentReference[oaicite:113]{index=113}
- [ ] Use design system/pattern library components where possible. :contentReference[oaicite:114]{index=114}
- [ ] Build a hi-fi prototype that:
  - [ ] Looks and feels realistic to users
  - [ ] Is quick to tweak

## Feedback & Culture Checklist

- [ ] Maintain:
  - [ ] Daily/regular design standups
  - [ ] Recurring design critiques
  - [ ] Retrospectives after each sprint/launch :contentReference[oaicite:115]{index=115}
- [ ] Ensure:
  - [ ] Work is posted in shared physical/digital spaces
  - [ ] Feedback language targets the design and goals
  - [ ] Juniors and seniors both present and critique
- [ ] Run blameless postmortems for major issues. :contentReference[oaicite:116]{index=116}

## Lateral Design & Visibility Checklist

- [ ] Cross-functional representation (design, engineering, product) on each initiative. :contentReference[oaicite:117]{index=117}
- [ ] Design values are documented and shared across org. :contentReference[oaicite:118]{index=118}
- [ ] Stakeholders have regular, informal access to design work (not just formal reviews). :contentReference[oaicite:119]{index=119}
- [ ] Designers routinely meet with:
  - [ ] Sales
  - [ ] Marketing
  - [ ] Customer support
  - [ ] Data science
  - [ ] Engineering :contentReference[oaicite:120]{index=120} :contentReference[oaicite:121]{index=121}

---

# Anti-Patterns

- Designing based on optimism and guesses instead of research (“product design lottery”). :contentReference[oaicite:122]{index=122} :contentReference[oaicite:123]{index=123}
- Over-surveying users; long, unfocused surveys. :contentReference[oaicite:124]{index=124} :contentReference[oaicite:125]{index=125}
- Relying purely on quantitative data without qualitative context (or vice versa). :contentReference[oaicite:126]{index=126}
- Jumping straight to hi-fi pixel-perfect design, making ideas too precious to change. :contentReference[oaicite:127]{index=127}
- Feedback deserts: no critique, no retrospectives, no visible work-in-progress. :contentReference[oaicite:128]{index=128}
- “Grand reveal” design in large orgs—no visibility until late, when changes are costly. :contentReference[oaicite:129]{index=129}
- Isolated design teams that don’t build relationships with other functions. :contentReference[oaicite:130]{index=130}

---

# Examples (Condensed Patterns)

- **Buffer:** over-invested in unvalidated features → layoffs and painful cuts → lesson: optimism without research is dangerous. :contentReference[oaicite:131]{index=131}
- **MailChimp:** quantitative data suggested value in Facebook integration; qualitative interviews revealed customers weren’t actually using it → changed course. :contentReference[oaicite:132]{index=132}
- **Bambora:** design team discovered rich, siloed NPS and customer visit data in operations → reused for product prioritization instead of creating new research. :contentReference[oaicite:133]{index=133}
- **Disney:** “pencil tests” let animators get fast feedback and refine continuously → analogy for high-fidelity prototypes. :contentReference[oaicite:134]{index=134} :contentReference[oaicite:135]{index=135}
- **Greater Good Studio:** project bays as physical spaces for posting work, enabling spontaneous critique. :contentReference[oaicite:136]{index=136}
- **Vox Media:** cheap remote testing rig (calendar, screen sharing, recording, team chat) → fast, distributed feedback loop. :contentReference[oaicite:137]{index=137}

---

# References (from the book)

The book cites (among others) these frameworks/resources:

- Jobs to Be Done (job stories) :contentReference[oaicite:138]{index=138}
- Design sprints and story-driven design :contentReference[oaicite:139]{index=139}
- Various texts on research, storytelling, and team organization (Lean UX, Sprint, Org Design for Design Orgs, etc.). :contentReference[oaicite:140]{index=140}

Use this distilled guideline as the operational layer; consult the original book for full context and narratives.
