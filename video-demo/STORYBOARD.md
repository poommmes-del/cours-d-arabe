---
format: 1920x1080
message: "A structured Arabic-learning library with real study evidence"
arc: Promise → Scale → Library → Learning flow → Evidence → Identity
audience: Hackathon judges and project visitors
mode: autonomous
duration: 27s
fps: 30
audio: none
---

# Cours d'arabe — 27-Second Silent Demo Storyboard

## Global direction

- **Format:** 1920×1080 landscape, 30 fps, 27.00 seconds.
- **Beat ownership:** exactly `0.00–3.00`, `3.00–7.00`, `7.00–13.00`, `13.00–19.00`, `19.00–24.00`, and `24.00–27.00`. Transition envelopes straddle boundaries, but copy and beat ownership switch at the exact boundary.
- **Audio:** None — no voiceover, music, ambience, or SFX.
- **Style basis:** `DESIGN.md`; deep blue-black canvas, raised navy surfaces, gold focus, restrained Nahw/Sarf/Balagha accents, Inter overlays, authentic Noto Naskh Arabic interface text.
- **Rhythm:** reveal → measure → explore → focus → evidence → resolve. Motion stays deliberate and educational; interface text remains readable.
- **Transition rule:** transitions own every non-final handoff. Beat elements remain composed and visible until the transition begins; no pre-transition fade, off-screen exit, or jump cut. Only Beat 6 may fade to black.
- **Capture rule:** Beats 3–5 use the real local 1920×1080 screenshots listed below. Do not redraw, translate, replace, or fabricate interface content.
- **Identity naming:** captured project identity is exactly `Cours d'arabe` (lowercase `a`). Beat 6's `Cours d'Arabe` (uppercase `A`) is approved closing script copy from `SCRIPT.md`, not a claim about captured wordmark spelling.
- **Entrance contract:** initialize every entrance with deterministic `gsap.fromTo()` on the single paused timeline. No `gsap.from()`, delayed setup, awaited load, or implicit CSS end state. A scene container may instead be introduced wholly by its named transition; all child entrances still use explicit `fromTo()` unless the transition fully owns that visible element.
- **Coordinate ownership:** annotations that point into a transformed screenshot are children of that screenshot's transform wrapper and use its native 1920×1080 coordinate system. Stage-level annotations use fixed precomputed 1920×1080 coordinates and never measure layout during a tween.
- **Safe bounds and overlay type:** informational overlays stay inside `x:96–1824`, `y:72–1008`. Headline overlays are at least 60 px, body copy at least 20 px, and labels at least 16 px. Captured UI is not re-typeset; active crops enlarge it where semantic reading is required.

### Overlay typography and bounds

| Beat | Overlay bounds | Exact type sizes |
| --- | --- | --- |
| 1 | headline `x:150 y:250 w:1460 h:330`; identity `x:150 y:112 w:620 h:90` | promise 104 px/0.96 line-height; `Cours d'arabe` 28 px; Arabic identity 32 px |
| 2 | statistic field `x:120 y:220 w:1680 h:610` | values 132 px; nouns 28 px; structural labels 18 px minimum |
| 3 | footer rail `x:120 y:846 w:1680 h:138` | category overlay 64 px; no other added text |
| 4 | copy panel `x:96 y:824 w:1100 h:150` | headline 64 px; no added body/label text |
| 5 | headline `x:96 y:76 w:940 h:96`; active crop `x:548 y:218 w:1276 h:620` | headline 68 px; active captured labels render at 16 px or larger after crop scaling |
| 6 | cadence `x:150 y:230 w:1620 h:170`; lockup `x:150 y:470 w:1500 h:300` | cadence 88 px; approved closing copy 104 px; Arabic identity 38 px |

### Declarative asset loading

- Declare each local font with CSS `@font-face` using the exact audited font-file URL listed below; declare matching weight/style and `font-display:block`.
- Preload used fonts and screenshots only with static `<link rel="preload" as="font|image">` declarations. No runtime `fetch()`, image promise, font promise, or JavaScript loader.
- Construct and register the paused root timeline synchronously during script evaluation: `window.__timelines[compositionId] = gsap.timeline({ paused:true })`. Do not put timeline creation or registration behind `await`, `async`, `Promise`, `setTimeout`, `document.fonts.ready`, or image callbacks.

## Captured screenshot audit

Every image under `capture/screenshots/` is assigned or explicitly skipped.

| Asset | Type | Assign to Beat | Role / reason |
| --- | --- | --- | --- |
| `capture/screenshots/scroll-000.png` | Catalogue hero capture | Beat 3 | Primary full-catalogue plane: identity header, metrics, search, RTL course grid, and all three discipline colors. |
| `capture/screenshots/scroll-100.png` | Catalogue lower-scroll capture | Beat 3 | Secondary depth plane revealing more Sarf and Balagha cards during the catalogue push. |
| `capture/screenshots/states/course.png` | Real course workspace | Beat 4 | Full learning-flow view: module list, audio player, lesson content, tabs, and progress controls. |
| `capture/screenshots/states/quiz.png` | Real questionnaire, collapsed | Beat 5 | Supporting “before” card behind the expanded correction; establishes multiple real questions. |
| `capture/screenshots/states/quiz-answer.png` | Real questionnaire, correction expanded | Beat 5 | First evidence focal card; real Arabic answer and `CORRIGÉ` state. |
| `capture/screenshots/states/resources.png` | Real Matn / Charh resources | Beat 5 | Second evidence focal card; three real local-resource actions. |
| `capture/screenshots/states/segments.png` | Real timestamped segments | Beat 5 | Third evidence focal card; transcript rows and time ranges. |
| `capture/screenshots/contact-sheet.jpg` | Diagnostic contact sheet | SKIP | Review-only composite of the two catalogue captures; lower resolution and duplicated content make it unsuitable for rendering. |

Utilization: 7/7 source screenshots and hero captures used; only derived contact sheet skipped. Opening uses exact captured `Cours d'arabe` identity from `scroll-000.png`; closing uses approved `Cours d'Arabe` script capitalization. Both are rebuilt with captured fonts so they stay sharp rather than enlarging a raster crop.

## Supporting capture asset audit

| Asset | Decision | Reason |
| --- | --- | --- |
| `capture/assets/svgs/svg-caa6f3cf.svg` | SKIP as standalone | Moon theme-control icon, not brand logo; already visible inside real captures. |
| `capture/assets/svgs/svg-d585a94c.svg` | SKIP as standalone | Sun theme-control icon, not brand logo and absent from dark-state story. |
| `capture/assets/svgs/contact-sheet.jpg` | SKIP | Diagnostic preview only, never a production visual. |
| `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf` | Beats 1, 2, 6 | Captured Inter ExtraBold 800 for primary English copy and counters. |
| `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf` | Beats 2–5 | Captured Inter SemiBold 600 for supporting overlay treatment. |
| `capture/assets/fonts/RrQ5bpV-9Dd1b1OAGA6M9PkyDuVBePeKNaxcsss0Y7bwWslkrA.ttf` | Beats 1, 6 | Captured Noto Naskh Arabic Bold 700 for `محمود الشافعي`. |

## BEAT 1 — PROMISE (0.00–3.00)

- scene: Project identity and learning promise assemble over a scholarly dark field
- duration: 3s
- transition_in: none
- status: outline
- poster: 2.2s

### Concept

Structure emerges from darkness like a carefully indexed manuscript. The project identity arrives first, then the promise assembles around a single gold rule; viewer should feel calm authority, not a loud launch ad.

### On-screen copy

`Arabic learning, finally structured.`

Identity: `محمود الشافعي` and `Cours d'arabe`.

### Visual description

A `#06090F` canvas carries a localized gold radial glow, faint manuscript-like guide lines, sparse deterministic dust, two registration corners, and the compact bilingual identity. “Arabic learning,” occupies the upper-left two-thirds; “finally structured.” locks beneath it against a short gold baseline. Nothing begins from black via a fade: the dark world already exists on frame one, with depth present while copy enters.

### Mood

Scholarly cinematic title sequence; measured museum-catalogue confidence with modern dashboard precision.

### Assets

- Identity reference: `capture/screenshots/scroll-000.png` — source for exact casing, hierarchy, and Arabic name; do not render a raster crop.
- English display: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf`.
- Arabic identity: `capture/assets/fonts/RrQ5bpV-9Dd1b1OAGA6M9PkyDuVBePeKNaxcsss0Y7bwWslkrA.ttf`.

### Techniques

1. Per-word kinetic typography for the two English clauses.
2. SVG path drawing for the baseline, guide rule, and registration corners.
3. Deterministic Canvas 2D procedural art for sparse gold dust; seeded coordinates only.

### Animation choreography

- `0.00–0.22`: canvas texture `fromTo(opacity:0→1)` REVEALS; radial glow `fromTo(opacity:0,scale:0.96→opacity:0.22,scale:1)` establishes depth, then BREATHES to 104% through `3.00`.
- `0.04–0.46`: each guide line `fromTo(scaleX:0,transformOrigin:left→scaleX:1)` DRAWS; seeded dust layer `fromTo(opacity:0→0.24)` appears before particles DRIFT less than 18 px.
- `0.12–0.48`: Arabic identity `fromTo(y:18,opacity:0→y:0,opacity:1)` DRAWS upward and LOCKS IN; `Cours d'arabe` uses `fromTo(x:28,opacity:0→x:0,opacity:1)` with `power2.out`.
- `0.35–0.90`: every “Arabic learning,” word uses explicit `fromTo(x:64→20 by index, y:14, opacity:0→x:0,y:0,opacity:1)` and ASSEMBLES in deterministic order.
- `0.82–1.34`: every “finally structured.” word uses explicit `fromTo(x:36→12 by index,y:10,opacity:0→x:0,y:0,opacity:1)` and SETTLES on same axis.
- `1.08–1.62`: gold baseline `fromTo(scaleX:0→1)` DRAWS; both registration corners use `fromTo(scale:0.7,opacity:0→scale:1,opacity:1)` and SNAP into alignment.
- `1.62–2.75`: complete identity and promise HOLD intact while background motion continues. No element animates out.

### Entrance ownership

- Base canvas, glow, guide lines, dust, Arabic identity, captured-case project name, both headline clauses, baseline, and both corner marks each have explicit synchronous `fromTo()` entrances above.
- Gold 1→2 cover is transition-owned and is not a Beat 1 content entrance.

### Transition

**Beat 1→2: gold clip-path wipe, `2.75–3.25`.** A full-frame `#F0B429` cover WIPES left-to-right using `clip-path: inset(0 100% 0 0) → inset(0 0 0 0)` over `0.25s power3.in`. At exact `3.00`, while gold fully covers frame, scene ownership swaps. Cover continues off right via `inset(0 0 0 100%)` over `0.25s power3.out`, revealing Beat 2. Transition overlay alone handles handoff; Beat 1 receives no exit tween.

### Depth layers

- **BG:** `#06090F`, localized gold radial glow, deterministic dust.
- **MG:** manuscript guide rules and large English promise.
- **FG:** bilingual project identity, gold baseline, registration corners.

### Audio

None.

## BEAT 2 — SCALE (3.00–7.00)

- scene: Three connected counters turn catalogue scale into a measured knowledge system
- duration: 4s
- transition_in: gold clip-path wipe
- status: outline
- poster: 5.4s

### Concept

The catalogue becomes a measured knowledge system. Three statistics behave like indexed volumes connected by one disciplined line, turning scale into proof of structure rather than spectacle.

### On-screen copy

`14 courses · 792 lessons · 664+ hours`

### Visual description

Three unequal raised panels span the frame on a deep navy field: courses left, lessons dominant in the center, hours right. Each panel contains a large tabular value, its noun, a thin discipline-colored top rule, and a small gold anchor node. A single SVG route links all three, while ghosted course-card outlines and low-contrast numeric ticks build an information-dense background without introducing new readable copy.

### Mood

Geometric, precise, archival data visualization; restrained Bauhaus rhythm translated into the captured dashboard language.

### Assets

- Counter font: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf`.
- Label font: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf`.
- No interface screenshot: this beat visualizes only approved statistics already visible in `capture/screenshots/scroll-000.png`.

### Techniques

1. SVG path drawing for the connecting route, nodes, and panel rules.
2. CSS 3D transforms for shallow perspective assembly of the three panels.
3. Per-word kinetic typography for the statistic nouns while GSAP proxies count values deterministically.

### Animation choreography

- `3.00–3.25`: Beat 2 container entrance is owned by gold wipe. All child start states are set synchronously at `3.00` beneath full gold; nothing completes unseen.
- `3.00–3.32`: background field `fromTo(opacity:0→1)` and ghost-card group `fromTo(y:18,opacity:0→y:0,opacity:0.16)` build under/revealed by cover. Numeric tick group uses `fromTo(opacity:0→0.22)`; ticks carry no semantic copy.
- Masked build timing follows wipe-clear direction: left panel begins `3.04`, center `3.12`, right `3.20`, only after cover edge reaches each precomputed x-zone. Each panel uses `fromTo(clipPath:inset(0 100% 0 0),rotationX:6,z:-80,opacity:0→clipPath:inset(0 0 0 0),rotationX:0,z:0,opacity:1)` and completes at `3.82`, `3.90`, `3.98` respectively.
- `3.36–4.55`: each value proxy deterministically COUNTS UP `0→14`, `0→792`, `0→664+`; each value glyph group first uses `fromTo(y:24,opacity:0→y:0,opacity:1)`. Nouns use `fromTo(x:24,opacity:0→x:0,opacity:1)` 120 ms later.
- `3.70–4.70`: every colored top rule uses `fromTo(scaleX:0→1)`; each gold node uses `fromTo(scale:0,opacity:0→scale:1,opacity:1)` with restrained `back.out(1.2)`.
- `4.15–5.20`: connector route uses `fromTo(strokeDashoffset:pathLength→0)` and LOCKS into nodes.
- `5.20–6.75`: panels FLOAT by alternating 4 px depth shifts; values and copy remain stable and readable. No element animates out.

### Entrance ownership

- Scene container is transition-owned from `3.00–3.25`; background field, ghost cards, ticks, all panels, values, nouns, rules, nodes, and connector path then use explicit synchronous `fromTo()` entrances.
- Gold cover is sole mask. Zone times above ensure left/center/right builds become visible as cover clears, avoiding hidden completed entrances.

### Transition

**Beat 2→3: blur through, `6.75–7.25`.** Transition controller defocuses the complete Beat 2 container `blur(0)→blur(20px)` and scales `1→1.02` over `0.25s power3.in`. At exact `7.00`, controller swaps to Beat 3 already at `blur(20px)`, `scale:0.98`; it clears to `blur(0)`, `scale:1` over `0.25s power3.out`. No opacity dip, pre-exit, or jump cut.

### Depth layers

- **BG:** deep navy field, faint numeric tick texture, ghosted card outlines.
- **MG:** three raised statistic panels and SVG connector route.
- **FG:** large values, labels, gold nodes, discipline-color rules.

### Audio

None.

## BEAT 3 — COURSE LIBRARY (7.00–13.00)

- scene: Camera explores the real RTL catalogue and its three discipline families
- duration: 6s
- transition_in: blur through
- status: outline
- poster: 10.8s

### Concept

The abstract scale resolves into the real catalogue. Viewer travels over a living RTL library, moving from project overview to authentic Arabic course cards while discipline colors become navigational landmarks.

### On-screen copy

`Nahw · Sarf · Balagha`

### Visual description

The unmodified `scroll-000.png` sits as the front plane of a shallow perspective stage, readable at full-frame scale. `scroll-100.png` sits behind and lower, exposed as the camera drifts toward the card grid; its overlap is hidden under the front plane rather than cut into view. Gold focus nodes and brackets are nested inside their respective screenshot-plane wrappers at native 1920×1080 coordinates, so they remain registered during plane transforms. A fixed stage-level dark glass footer rail carries the exact 64 px three-word overlay while the captured header, metrics, Arabic titles, and cards remain visible.

### Mood

Premium product tour with documentary respect for the real interface; quiet forward motion, no synthetic UI embellishment.

### Assets

- Primary interface: `capture/screenshots/scroll-000.png` — uncropped 1920×1080 front plane.
- Secondary interface: `capture/screenshots/scroll-100.png` — lower-catalogue depth plane.
- Overlay font: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf`.

### Techniques

1. CSS 3D transforms for the two captured catalogue planes and controlled camera push.
2. GSAP MotionPathPlugin for the gold focus node across real discipline badges.
3. SVG path drawing for the focus route and three restrained callout brackets.

### Animation choreography

- `7.00–7.25`: catalogue clears from transition blur; front capture is already correctly framed, never popped in.
- `7.18–9.10`: camera PUSHES from `scale:0.98` to `1.055` with a 2° perspective settle, preserving header and first card rows.
- `8.00–10.80`: focus node TRAVELS on one curved SVG route; green, violet, then orange brackets DRAW around existing category badges as node reaches each zone.
- `9.20–11.35`: front plane GLIDES 110 px upward and 90 px left, exposing the lower `scroll-100.png` plane at the right/bottom edge; both captures stay visible, so no internal cut occurs.
- `9.70–11.60`: “Nahw · Sarf · Balagha” BUILDS token by token on the glass footer rail; category words use only their captured semantic colors.
- `11.60–12.75`: camera SETTLES; both screenshot planes, route, and overlay HOLD intact. No element animates out.

### Coordinate ownership

- Front-capture route, Nahw/Sarf brackets, and their node are children of `scroll-000` wrapper; lower-capture Balagha bracket/node are children of `scroll-100` wrapper. All use fixed source coordinates measured once from 1920×1080 captures.
- Footer rail and 64 px overlay are stage-owned at fixed `x:120 y:846 w:1680 h:138`; they never inherit screenshot scale or pan.

### Transition

**Beat 3→4: CSS cinematic zoom, `12.75–13.25`.** The catalogue scales `1→1.16` with `blur(0→16px)` over `0.25s power2.in`; at exact `13.00`, the Ajroumiya workspace takes ownership at `scale:0.84`, `blur(16px)` and clears to `scale:1`, `blur(0)` over `0.25s power2.out`. Radial zoom blur pulls the catalogue center into the workspace. The CSS transition owns entire exit/entry; no scene-level exit tween.

### Depth layers

- **BG:** `#06090F` stage and secondary lower-scroll capture.
- **MG:** primary catalogue capture in shallow 3D perspective.
- **FG:** glass copy rail, gold route/node, category brackets.

### Audio

None.

## BEAT 4 — LEARNING FLOW (13.00–19.00)

- scene: A gold guide tours the real course workspace from audio to progress
- duration: 6s
- transition_in: CSS cinematic zoom
- status: outline
- poster: 17.8s

### Concept

The catalogue opens into a complete study desk. Instead of replacing the interface with explanatory graphics, one precise gold guide tours the real workspace: listen, choose a module, read the structured lesson, then mark progress.

### On-screen copy

`Listen. Understand. Track progress.`

### Visual description

`course.png` fills the frame inside a narrow raised border. Its audio player, left module rail, Arabic lesson body, tabs, and progress controls stay authentic and legible. Focus route, ring, brackets, veils, and progress underline are children of the screenshot transform wrapper at fixed native coordinates, so every annotation follows the 1.00→1.045 camera push. The 64 px overlay is stage-owned on a compact lower-left glass panel, away from the main Arabic lesson copy.

### Mood

Focused study-session calm; editorial guided tour, like a patient instructor pointing without interrupting the page.

### Assets

- Real interface: `capture/screenshots/states/course.png` — full 1920×1080 Ajroumiya workspace.
- Overlay font: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf`.

### Techniques

1. CSS 3D transforms for a slow, shallow camera push on the captured workspace.
2. GSAP MotionPathPlugin for the focus ring’s four-stop guided route.
3. SVG path drawing for focus boxes, route, and progress underline.

### Animation choreography

- `13.00–13.25`: course workspace container entrance is wholly transition-owned by CSS cinematic zoom; screenshot remains dominant full-frame source. Border separately uses `fromTo(opacity:0,scale:0.995→opacity:1,scale:1)` as transition blur clears.
- `13.24–18.75`: screenshot DRIFTS from `scale:1.00` to `1.045` with less than 45 px total pan, retaining all major zones.
- `13.28–13.62`: stage-owned copy panel uses `fromTo(x:-36,opacity:0→x:0,opacity:1)`; focus-ring uses `fromTo(scale:0,opacity:0→scale:1,opacity:1)`; route uses `fromTo(strokeDashoffset:pathLength→0)` only through first stop.
- `13.45–14.35`: audio bracket uses `fromTo(strokeDashoffset:length,opacity:0→0,opacity:1)`; audio veil uses `fromTo(opacity:0→0.14)` around, never over, controls. “Listen.” uses `fromTo(x:30,opacity:0→x:0,opacity:1)` inside 64 px headline.
- `14.35–15.55`: ring TRAVELS to selected module on precomputed path; module bracket uses explicit dashoffset `fromTo`; module veil uses `fromTo(opacity:0→0.12)` while left rail stays readable.
- `15.55–17.05`: ring TRAVELS to lesson headings; “Understand.” uses `fromTo(y:22,opacity:0→y:0,opacity:1)`; lesson bracket and veil use explicit dashoffset/opacity `fromTo()` around central reading zone.
- `17.05–18.20`: ring TRAVELS to progress controls; “Track progress.” uses `fromTo(x:28,opacity:0→x:0,opacity:1)`; progress bracket uses dashoffset `fromTo()` and underline uses `fromTo(scaleX:0→1)`.
- `18.20–18.75`: complete route, screenshot, and copy HOLD intact. No element animates out.

### Entrance ownership

- Screenshot container is CSS-cinematic-transition-owned; border, copy panel, all three copy tokens, focus ring, route, four brackets, four localized veils, and progress underline each receive explicit deterministic `fromTo()` entrances.
- Every interface annotation is screenshot-wrapper-owned at native coordinates; only copy panel/headline is fixed stage-owned at `x:96 y:824 w:1100 h:150`.

### Transition

**Beat 4→5: blur through, `18.75–19.25`.** Transition controller defocuses complete Beat 4 `blur(0)→blur(20px)`, `scale:1→1.02` over `0.25s power3.in`; at exact `19.00`, it swaps to the prepared evidence-card stage at `blur(20px)`, `scale:0.98`, then clears over `0.25s power3.out`. No opacity dip or independent screenshot exit.

### Depth layers

- **BG:** full real course workspace and its original dark surfaces.
- **MG:** SVG route and four localized focus brackets.
- **FG:** traveling focus ring, lower-left copy panel, progress underline.

### Audio

None.

## BEAT 5 — STUDY TOOLS (19.00–24.00)

- scene: Readable real evidence states move through one persistent study desk
- duration: 5s
- transition_in: blur through
- status: outline
- poster: 22.7s

### Concept

Evidence fans out as a connected study trail, not a rapid slideshow. Four real states remain present on one 3D desk while focus shifts from question to correction, source materials, and timestamped transcript.

### On-screen copy

`Practice with evidence.`

### Visual description

Four screenshot cards occupy one perspective stage: collapsed `quiz.png` stays a context thumbnail, while readable source crops from `quiz-answer.png`, `resources.png`, and `segments.png` take turns in one fixed `1276×620` active window. Non-active cards remain visible only as 280×136 cropped context thumbnails; they carry no semantic reading requirement. Each active crop holds sharp at enlarged scale before focus moves. Gold brackets are children of each card wrapper; the stage-owned evidence thread uses fixed endpoints for active-window and thumbnail slots. Exact 68 px overlay anchors high-left, clear of screenshot content.

### Mood

Research desk meets product proof; quick enough to show breadth, slow enough to identify every authentic state.

### Assets

- Questionnaire context: `capture/screenshots/states/quiz.png`.
- Expanded correction: `capture/screenshots/states/quiz-answer.png`.
- Local resources: `capture/screenshots/states/resources.png`.
- Timestamped evidence: `capture/screenshots/states/segments.png`.
- Overlay font: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf`.

### Techniques

1. CSS 3D transforms for persistent layered screenshot cards and rack-focus depth.
2. GSAP MotionPathPlugin for the traveling gold evidence node.
3. SVG path drawing for the evidence thread and per-card focus brackets.

### Animation choreography

- `19.00–19.25`: Beat 5 stage-container entrance is transition-owned by blur through. Radial field separately uses `fromTo(opacity:0,scale:0.98→opacity:0.18,scale:1)` as blur clears.
- `19.22–19.44`: each card uses two wrappers. Outer `.card-enter` owns entrance only and completes `fromTo(y:26,opacity:0→y:0,opacity:1)` before focus begins. Inner `.card-focus` owns all fixed `x/y/scale/rotationY/z/filter` context geometry below; no property is animated simultaneously on parent and child. All cards settle into 280×136 context slots by `19.44`.
- `19.32–19.68`: 68 px headline uses three deterministic `fromTo(x:36→16 by group,opacity:0→x:0,opacity:1)` entries. Stage evidence thread begins with `fromTo(strokeDashoffset:pathLength→firstStop)`; focus node uses `fromTo(scale:0,opacity:0→scale:1,opacity:1)`.
- `19.45–19.70`: after outer entrance is complete, `quiz-answer.png` inner `.card-focus` uses `fromTo(x:128,y:322,scale:0.259,rotationY:-7,z:-80,filter:blur(2px)→x:548,y:218,scale:1.181,rotationY:0,z:0,filter:blur(0px))`; nested gold bracket uses dashoffset/opacity `fromTo()` around `CORRIGÉ`.
- `19.70–20.65`: expanded-correction crop HOLDS sharp and stationary for `0.95s`; collapsed `quiz.png` remains context only.
- `20.65–20.92`: focus node TRAVELS to resources endpoint; `resources.png` uses `fromTo(x:248,y:512,scale:0.233,rotationY:-4,z:-70,filter:blur(2px)→x:548,y:218,scale:1.063,rotationY:0,z:0,filter:blur(0px))` while prior active card deterministically returns to context without disappearing.
- `20.92–21.75`: resource crop HOLDS sharp and stationary for `0.83s`; nested bracket DRAWS around three real resource rows.
- `21.75–22.02`: focus node TRAVELS from top-right segments endpoint; `segments.png` uses `fromTo(x:1520,y:72,scale:0.255,rotationY:6,z:-70,filter:blur(2px)→x:548,y:218,scale:1.160,rotationY:0,z:0,filter:blur(0px))` while resource card returns to context.
- `22.02–23.20`: segment crop HOLDS sharp and stationary for `1.18s`; nested bracket DRAWS down real timestamp rows and evidence thread completes to final endpoint.
- `23.20–23.75`: all four capture cards, thread, and copy HOLD as a resolved evidence system. No element animates out.

### Readability and crop plan

- Active window is fixed at `x:548 y:218 w:1276 h:620`, inside safe bounds. No overlay crosses it.
- Every context window is exactly 280×136. Fixed slots: `quiz.png x:96 y:820 source crop (420,260,1200,583) scale:0.233 rotationY:-8 z:-90`; `quiz-answer.png x:128 y:322 scale:0.259 rotationY:-7 z:-80`; `resources.png x:248 y:512 scale:0.233 rotationY:-4 z:-70`; `segments.png x:1520 y:72 w:280 h:136 scale:0.255 rotationY:6 z:-70`. Segments slot ends at `y:208`, leaving 10 px before active window starts at `y:218`; it starts right of headline end `x:1036`.
- Expanded correction uses source crop `x:420 y:260 w:1080 h:525`, rendered at `1.18×`; correction text is semantic focus.
- Resources uses source crop `x:420 y:260 w:1200 h:583`, rendered at `1.06×`; original 16 px actions render at about 17 px.
- Segments uses source crop `x:420 y:260 w:1100 h:535`, rendered at `1.16×`; timestamps and Arabic rows are semantic focus.
- `quiz.png` and every non-active state remain 280×136, `opacity:0.42`, `blur:2px`, context only. Never ask viewer to read thumbnail text.

### Entrance ownership

- Stage container is blur-transition-owned; radial field, headline groups, four outer `.card-enter` wrappers, focus node, evidence thread, and every nested bracket use explicit deterministic `fromTo()` entrances. Inner `.card-focus` wrappers exclusively own card focus geometry.
- Each bracket is nested in its source card wrapper and uses source-crop coordinates. Evidence thread is stage-owned with fixed precomputed slot endpoints; no tween-time DOM measurement.

### Transition

**Beat 5→6: gold clip-path wipe, `23.75–24.25`.** Full-frame `#F0B429` cover WIPES left-to-right with `clip-path: inset(0 100% 0 0) → inset(0 0 0 0)` over `0.25s power3.in`. Scene ownership swaps at exact `24.00` under full gold. Cover clears right via `inset(0 0 0 100%)` over `0.25s power3.out`, revealing closing identity. Cards receive no exit tween.

### Depth layers

- **BG:** deep navy stage with faint radial gold illumination.
- **MG:** four real screenshot cards in shallow 3D fan.
- **FG:** evidence thread, moving node, focus brackets, exact overlay copy.

### Audio

None.

## BEAT 6 — CLOSING (24.00–27.00)

- scene: Approved closing cadence resolves to project identity and holds
- duration: 3s
- transition_in: gold clip-path wipe
- status: outline
- poster: 26.1s

### Concept

The evidence condenses back into one memorable learning loop. Promise becomes cadence—learn, practice, progress—then resolves to the same project identity that opened the film.

### On-screen copy

`Learn. Practice. Progress.`

`Cours d'Arabe` — approved closing script copy from `SCRIPT.md`; captured identity elsewhere remains `Cours d'arabe`.

Identity: `محمود الشافعي`.

### Visual description

Gold wipe reveals the original deep canvas with a restrained radial halo, three fine concentric study rings, and a short structural rule. “Learn. Practice. Progress.” spans the upper two-thirds; each verb lands on one ring node. Approved script closing copy `Cours d'Arabe` resolves large beneath it, with `محمود الشافعي` as authentic Arabic signature. This capitalization is intentionally script copy; captured wordmark remains `Cours d'arabe`. Registration corners and sparse dust echo Beat 1, completing a visual loop.

### Mood

Quiet thesis and earned resolution; premium scholarly end card, confident enough to hold.

### Assets

- Identity reference: `capture/screenshots/scroll-000.png` — captured spelling `Cours d'arabe`; do not render raster crop. Closing `Cours d'Arabe` comes verbatim from approved `SCRIPT.md`.
- English display: `capture/assets/fonts/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf`.
- Arabic identity: `capture/assets/fonts/RrQ5bpV-9Dd1b1OAGA6M9PkyDuVBePeKNaxcsss0Y7bwWslkrA.ttf`.

### Techniques

1. Per-word kinetic typography for the three-verb cadence and project name.
2. SVG path drawing for study rings, node connectors, baseline, and registration corners.
3. Deterministic Canvas 2D procedural art for the returning sparse dust field.

### Animation choreography

- `24.00–24.25`: gold cover clears; closing canvas and halo are already present beneath it.
- `24.12–24.70`: three study rings DRAW concentrically; nodes POP in sequence and dust DRIFTS with Beat 1’s seeded pattern.
- `24.30–24.95`: “Learn.”, “Practice.”, and “Progress.” LAND one by one with decaying vertical offsets `48→18 px`; each node PULSES once as its verb lands.
- `24.86–25.25`: approved script copy `Cours d'Arabe` ASSEMBLES from a 24 px rise; gold baseline FILLS beneath it.
- `25.05–25.38`: `محمود الشافعي` DRAWS upward and LOCKS beneath project name; registration corners SNAP into place.
- `25.38–26.75`: completed brand lockup HOLDS fully readable for `1.37s`.
- `26.75–27.00`: final-scene-only fade lowers complete frame opacity to black with `sine.inOut`. This is the only non-transition exit in the video.

### Transition

Final closure only: `26.75–27.00` fade to black. No next beat and no jump cut.

### Depth layers

- **BG:** `#06090F`, localized gold halo, deterministic dust.
- **MG:** three SVG study rings and large three-verb cadence.
- **FG:** project name, Arabic identity, gold baseline, registration corners.

### Audio

None.

## Implementation handoff

- Build one root timeline with six scene containers and exact total duration `27.00`.
- Use literal palette values on transitioning elements; every scene gets explicit `background-color:#06090F` or its documented dark surface.
- Keep screenshot pixels unmodified except transform, crop/mask, border, shadow, and transition filters. No fake interaction states.
- Declare static preloads and `@font-face` rules in document head, then construct/register paused timeline synchronously in script evaluation; never await font/image readiness before registration.
- All entrance states must be explicit and deterministic. No `Math.random`, `Date.now`, infinite repeats, manual media playback, or network fetches.
- Transition controller performs every non-final handoff. Scene choreography contains entrances, focus movement, ambient holds, and no pre-transition exits.
