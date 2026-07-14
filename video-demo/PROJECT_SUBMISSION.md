# Project Story

## Inspiration

Arabic students often have the opposite of a content problem: they have long audio lessons, classical texts, commentaries, transcripts, and exercises, but no clear path through them. I built **Cours d'Arabe** to turn that fragmented material into a structured, local-first learning experience.

The goal was simple: help learners move from listening to understanding, then from understanding to deliberate practice. Instead of replacing traditional resources, the project connects them—audio lessons, pedagogical modules, quizzes, *matn*, *sharh*, transcripts, and timestamped segments—inside one focused interface.

## What it does

Cours d'Arabe organizes **14 courses**, **792 lessons**, and more than **664 hours** of instruction across Arabic grammar (*nahw*), morphology (*sarf*), and rhetoric (*balagha*).

Each course is rebuilt into concept-based modules with:

- clear learning objectives;
- structured explanations and examples;
- practice exercises and answer corrections;
- compressed lesson audio;
- raw transcripts and clickable timestamps;
- local *matn* and *sharh* PDFs;
- persistent learning progress.

Everything runs locally, so the library remains available without depending on a remote platform during study.

## How I built it

I designed the project as a reproducible content pipeline rather than a collection of manually linked files.

Python tools inventory the source lessons, validate transcripts and audio, assemble transcript-first pedagogical modules, connect book resources, and generate a single JSON catalog for the interface. The frontend is a lightweight HTML, CSS, and JavaScript application with right-to-left Arabic support, larger Arabic typography, quizzes, local progress tracking, and timestamp-based audio navigation.

To reduce storage while preserving speech clarity, I converted the source audio to mono Opus at 24 kb/s. The approximate storage reduction is:

$$
R = 1 - \frac{6.5}{29.26} \approx 77.8\%
$$

Automated Python and Playwright tests protect the integrity of all 14 courses: lesson counts, local assets, transcripts, PDFs, module quality, quiz behavior, tab order, Arabic rendering, and catalog consistency.

I created the silent 27-second product demo with HyperFrames and GSAP. It uses deterministic, seekable animation and real screenshots from the application to show the journey from course discovery to listening, practice, evidence, and progress.

## Challenges

The hardest challenge was turning hundreds of hours of source material into a coherent curriculum without presenting raw transcripts as finished lessons. Each module needed to follow the progression of its source book while remaining readable, practical, and traceable to the relevant audio and references.

Data integrity was another major challenge. With 792 lessons and several resource types per course, one missing transcript, audio file, or PDF could quietly break the experience. I addressed this with strict manifests, generated catalogs, protected source mappings, and tests that fail when expected material is missing or inconsistent.

For the demo, the main challenge was reliable timeline seeking across nested compositions. I removed a runtime shader canvas that interfered with inspection, replaced it with a deterministic CSS cinematic zoom, and corrected two GSAP initialization states so forward and backward seeks produce identical measured timeline and DOM state.

## What I learned

I learned that educational structure matters as much as content volume. A large archive becomes useful only when learners can see what to study, why it matters, how to practice it, and where to verify it in the source material.

I also learned the value of treating content like software: explicit schemas, reproducible builds, immutable source evidence, automated quality gates, and browser-level tests make a large learning library far easier to trust and evolve.

## What's next

Next steps include stronger search across Arabic concepts, richer progress analytics, spaced-repetition review queues, and more learner-focused accessibility controls—while preserving the project's local-first, source-grounded approach.

# Built with

`Python` `JavaScript` `HTML5` `CSS3` `Markdown` `JSON` `Playwright` `Deepgram` `FFmpeg` `Opus` `Archive.org` `localStorage` `RTL` `HyperFrames` `GSAP`

# Video demo link

https://www.youtube.com/watch?v=IEp2CNY-M2E
