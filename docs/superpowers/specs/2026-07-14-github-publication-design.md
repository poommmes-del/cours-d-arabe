# GitHub Publication Design

## Goal

Publish a public, Devpost-ready source repository at
`https://github.com/poommmes-del/cours-d-arabe` without uploading the project's
multi-gigabyte generated media corpus.

## Chosen approach

Use the remote repository's empty default branch as `main` and push one curated
source snapshot directly. The repository will contain the application source,
content-generation tools, tests, pedagogical Markdown, generated catalog,
project documentation, and reproducible HyperFrames demo source.

The following local-only or generated data will be excluded:

- `audios-opus/` (about 6.5 GB);
- `archive-items/` (about 1.7 GB, including raw transcriptions);
- `livres/` (about 449 MB, including PDFs and OCR data);
- HyperFrames renders, captures, snapshots, thumbnails, and dependencies;
- agent state, CodeGraph indexes, caches, test output, and Vercel metadata.

This avoids GitHub's regular-file limits and keeps source review practical. The
full media-backed experience remains available through the existing Vercel demo.

## README

Replace the outdated French README with an English-first Devpost README. It will
include:

- live demo and project metrics: 14 courses, 792 lessons, 604 modules, 4,918
  questions, and 664:49:30 of audio;
- product story, architecture, repository layout, local setup, and verification;
- a prominent, specific section explaining how Codex and GPT-5.6 contributed;
- a transparent note that large audio, transcript archives, and PDFs are not
  stored in GitHub.

## Validation and publication

Before committing the source snapshot:

1. run the complete Python test suite and JavaScript syntax check;
2. inspect staged files for secrets and files larger than 10 MB;
3. confirm excluded directories are absent from the Git index;
4. push `main` to `origin`;
5. verify the GitHub repository, README, default branch, and live demo link.

## Failure handling

Stop before push if tests fail, secrets are detected, or oversized files are
staged. If the remote stops being empty, fetch it and reconcile histories rather
than force-pushing.
