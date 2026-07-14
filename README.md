# Cours d'Arabe — Structured Classical Arabic Learning

[![Live demo](https://img.shields.io/badge/Live_demo-Vercel-000000?logo=vercel)](https://cours-arabe-xi.vercel.app)
[![Courses](https://img.shields.io/badge/courses-14-C49A45)](#at-a-glance)
[![Lessons](https://img.shields.io/badge/audio_lessons-792-C49A45)](#at-a-glance)

Cours d'Arabe turns a large archive of Arabic audio lessons, classical texts,
commentaries, and transcripts into a guided learning experience for *nahw*
(grammar), *sarf* (morphology), and *balagha* (rhetoric).

**[Open the live application](https://cours-arabe-xi.vercel.app)**

## Video demo

[![Watch the silent Cours d'Arabe product demo](https://img.youtube.com/vi/IEp2CNY-M2E/maxresdefault.jpg)](https://www.youtube.com/watch?v=IEp2CNY-M2E)

**[Watch the sub-30-second demo on YouTube](https://www.youtube.com/watch?v=IEp2CNY-M2E)**

## At a glance

| Content | Total |
|---|---:|
| Courses | 14 |
| Audio lessons | 792 |
| Pedagogical modules | 604 |
| Review questions | 4,918 |
| Audio duration | 664:49:30 |

The project does more than display raw transcripts. It rebuilds each course as
a sequence of concept-based modules with objectives, explanations, tables,
worked examples, practice, questions, source references, and precise audio
spans.

## Why I built it

Arabic learners often have an abundance of material but no clear path through
it. A single subject may involve dozens of long recordings, a *matn*, one or
more *sharh* volumes, transcripts, and separate exercises. Cours d'Arabe brings
those pieces into one focused interface while preserving their connection to
the original sources.

The learning loop is:

1. choose a course and concept;
2. read a structured explanation;
3. listen to the exact relevant lesson span;
4. practise and answer review questions;
5. verify the concept in the transcript, *matn*, or *sharh*;
6. keep progress locally in the browser.

## Core features

- 14 curricula across grammar, morphology, and rhetoric;
- concept-based modules instead of arbitrary audio batches;
- lesson-aware audio playback with module-specific timestamp seeking;
- quizzes with corrections and persistent progress;
- raw transcripts and clickable segments for source verification;
- local *matn* and *sharh* resources;
- beginner-friendly Arabic typography, RTL layout, and vocalised examples;
- static, dependency-light frontend with no account required.

## How it was built

Python tools inventory the source lessons, validate transcripts and compressed
audio, assemble transcript-first pedagogical modules, connect book resources,
and generate one JSON catalog. A lightweight HTML/CSS/JavaScript frontend reads
that catalog and provides navigation, quizzes, audio seeking, source material,
and local progress tracking.

Audio was converted to mono Opus at 24 kb/s. Storage changed from approximately
29.26 GB of source material to 6.5 GB:

$$
R = 1 - \frac{6.5}{29.26} \approx 77.8\%
$$

Python and Playwright regression tests validate course counts, source mappings,
asset integrity, module quality, quiz behaviour, Arabic rendering, tab order,
and audio navigation.

## How Codex and GPT-5.6 were used

This project used **OpenAI Codex** and **GPT-5.6** as active development and
content-engineering collaborators—not as runtime dependencies.

**Codex helped build and verify the product:**

- explored and mapped the existing content pipeline;
- implemented Python generators, validation rules, and frontend behaviour;
- diagnosed the lesson-mapping bug that made every module play the same audio;
- added regression tests for timestamp and lesson selection across all courses;
- ran repository-wide checks and prepared the Vercel deployment;
- developed the deterministic HyperFrames product-demo source.

**GPT-5.6 helped structure the educational corpus:**

- transformed transcript evidence into concept-based module drafts;
- organised explanations, examples, exercises, and review questions;
- preserved traceability through per-course source maps and audio spans;
- helped maintain consistent pedagogical structure across hundreds of modules;
- assisted with technical writing and presentation material.

Human review remained the final quality gate for curriculum decisions, Arabic
content, source alignment, product behaviour, and publication. No model call is
required to use the deployed application.

## Architecture

```text
Source audio + transcripts + books
                |
                v
      Python validation/build tools
                |
                v
       site/data/catalog.json
                |
                v
    Static HTML/CSS/JS application
                |
                v
 Audio + modules + quizzes + sources
```

| Path | Purpose |
|---|---|
| `site/` | Static application and generated catalog |
| `cours-pedagogiques/` | Course Markdown, modules, and source maps |
| `outils/` | Content build, validation, compression, and import tools |
| `tests/` | Python and browser regression tests |
| `video-demo/` | HyperFrames/GSAP demo source and submission story |
| `docs/` | Design specifications and implementation plans |

## Repository data boundary

This GitHub repository intentionally contains reviewable source, tests, and
pedagogical Markdown—not the multi-gigabyte binary corpus.

Excluded from Git:

- 6.5 GB of compressed lesson audio;
- 1.7 GB of raw archive data and transcripts;
- 449 MB of PDFs, OCR output, and book assets;
- generated video renders, screenshots, caches, and agent state.

These files exceed practical GitHub repository and regular-file limits. The
full deployed experience, including all 792 audio lessons, is available in the
[live demo](https://cours-arabe-xi.vercel.app).

## Run the source locally

Requirements: Python 3.11+ and Node.js 20+ for validation.

```bash
python3 -m http.server 8766
```

Then open:

```text
http://127.0.0.1:8766/site/
```

The interface and generated catalog load from this source checkout. Audio,
transcript archives, and PDFs require the excluded local corpus; use the live
deployment for the complete media-backed experience.

## Rebuild and verify

Generate the catalog when the local media corpus is available:

```bash
python3 outils/generate_site_data.py
```

Run the core checks:

```bash
python3 -m unittest discover -s tests
node --check site/assets/app.js
```

Selected browser tests can be run with Playwright against a local server:

```bash
npx --yes -p @playwright/test@latest bash -lc \
  'BIN_DIR=$(dirname "$(which playwright)"); \
   export NODE_PATH=$(dirname "$BIN_DIR"); \
   playwright test tests/ui_ajroumiya_course.spec.js \
   tests/ui_quiz.spec.js --browser=chromium --reporter=line'
```

## Product demo

The [silent, sub-30-second product video](https://www.youtube.com/watch?v=IEp2CNY-M2E)
was built with HyperFrames and GSAP.
Composition source, storyboard, script, and Devpost project story live in
[`video-demo/`](video-demo/). Generated MP4 and inspection captures remain
outside Git.

## Next steps

- concept search across Arabic terminology;
- richer progress analytics;
- spaced-repetition review queues;
- stronger learner accessibility controls;
- reproducible external storage manifests for the large media corpus.
