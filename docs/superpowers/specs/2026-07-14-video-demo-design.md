# Cours d'Arabe — 27-Second Video Demo Design

## Goal

Create an upload-ready, silent product demo for the project presentation page. The video must communicate the project's scale, show the real interface, and explain the learning flow in 30 seconds or less without narration or music.

## Audience and Format

- Audience: hackathon judges and visitors discovering the project.
- Language: English interface overlays; authentic Arabic course content remains visible.
- Format: 1920×1080 landscape, H.264 MP4, 30 fps.
- Target duration: 27 seconds; hard maximum: 30 seconds.
- Audio: none.

## Creative Direction

Use a hybrid of kinetic typography and real interface captures. Preserve the application's premium dark visual identity: near-black navy backgrounds, translucent glass surfaces, warm gold accents, and restrained category colors.

Typography uses Inter for English overlays and Noto Naskh Arabic for Arabic content. Motion feels fluid, focused, and educational rather than loud. Camera movement uses slow pushes and deliberate pans. Transitions use gold wipes or soft crossfades; no jump cuts.

## Visual Identity

- Canvas: `#06090f` and `#0c1119`.
- Surface: `#131b28` with translucent white borders.
- Primary text: `#f8fafc`.
- Secondary text: `#94a3b8`.
- Accent: `#f0b429` with `#f7c948` highlights.
- Category accents: Nahw `#34d399`, Sarf `#a78bfa`, Balagha `#fb923c`.
- English font: Inter.
- Arabic font: Noto Naskh Arabic.

Avoid generic blue SaaS styling, excessive glow, rapid cuts, fake interface elements, light-theme shots, and decorative motion that competes with Arabic text.

## Storyboard

### Beat 1 — Promise, 0:00–0:03

Dark canvas with subtle gold radial light. English headline enters in two controlled movements: “Arabic learning,” then “finally structured.” A small Arabic wordmark establishes the subject.

### Beat 2 — Scale, 0:03–0:07

Three large counters appear with staggered motion: “14 courses”, “792 lessons”, and “664+ hours”. Fine connector lines and small labels suggest a structured library rather than disconnected files.

### Beat 3 — Course Library, 0:07–0:13

Show a real capture of the home catalogue. Camera pushes toward RTL course cards while concise labels identify Nahw, Sarf, and Balagha. Keep course titles and application statistics readable.

### Beat 4 — Learning Flow, 0:13–0:19

Transition into a real course view. Focus sequentially on the audio player, module list, structured Arabic lesson, and progress controls. Overlay: “Listen. Understand. Track progress.”

### Beat 5 — Study Tools, 0:19–0:24

Show fast but readable views of questionnaire answers, Matn/Charh resources, and timestamped transcript segments. Overlay: “Practice with evidence.”

### Beat 6 — Closing, 0:24–0:27

Return to branded dark canvas. Final line: “Learn. Practice. Progress.” Resolve to “Cours d’Arabe” with the Arabic course identity below it.

## Capture and Composition Architecture

Run the existing static site locally and capture key interface states at 1920×1080. Use HyperFrames as the source of truth for the final composition. Store captures as local assets; do not depend on the running site during final rendering.

One root HyperFrames composition controls six timed scene clips. Each scene has its own entrance choreography. Transitions own all non-final exits. No infinite animation loops or non-deterministic motion.

## Text and Timing Rules

- Keep each English message below seven words.
- Headlines must remain at least 60 px in rendered output.
- Hold every key interface state long enough to identify its purpose.
- Use entrance animations for every visible scene element.
- Use no pre-transition exit animations; final scene may fade to black.

## Validation

- HyperFrames lint and validate must report zero errors.
- Visual inspection must show no overflow, clipped copy, or unintended overlap.
- Contrast must meet WCAG AA for all informational text.
- Animation map must show intended entrances, transitions, and no accidental dead zones.
- Final MP4 must be 1920×1080, 30 fps, silent, and no longer than 30 seconds.
- Review snapshots at approximately 1.5, 5, 10, 16, 22, and 26 seconds before final render.

## Delivery

Deliver the HyperFrames project, active local Studio preview URL, and rendered MP4. External hosting is outside repository scope; the MP4 can be uploaded to YouTube or Vimeo to obtain the presentation-page video link.
