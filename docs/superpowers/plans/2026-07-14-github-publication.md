# GitHub Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a curated, Devpost-ready source snapshot to `poommmes-del/cours-d-arabe`.

**Architecture:** Track source code and pedagogical Markdown in Git while excluding multi-gigabyte generated media and private agent state. Present the deployed product and AI-assisted workflow through an English-first README.

**Tech Stack:** Git, GitHub CLI, Markdown, Python unittest, Node.js, Vercel

## Global Constraints

- Push directly to `main` because the target repository is empty and the user explicitly requested publication there.
- Never stage `audios-opus/`, `archive-items/`, `livres/`, `.superpowers/`, caches, or rendered video assets.
- Keep `site/data/catalog.json` so reviewers can inspect the complete generated content model.
- Mention Codex and GPT-5.6 explicitly in the README.

---

### Task 1: Curate the repository

**Files:**
- Create: `.gitignore`
- Modify: `README.md`
- Create: `docs/superpowers/specs/2026-07-14-github-publication-design.md`
- Create: `docs/superpowers/plans/2026-07-14-github-publication.md`

**Interfaces:**
- Consumes: current application source and `site/data/catalog.json` metrics
- Produces: reviewable repository root and explicit inclusion boundaries

- [ ] **Step 1: Add exact exclusions**

Create `.gitignore` entries for local media corpora, agent state, caches,
deployment metadata, and HyperFrames outputs while retaining demo source HTML.

- [ ] **Step 2: Replace README**

Write English project documentation with live demo, architecture, setup, tests,
data-boundary disclosure, and a `How Codex and GPT-5.6 were used` section.

- [ ] **Step 3: Inspect tracked scope**

Run:

```bash
git status --short --ignored
git ls-files
```

Expected: source directories visible; excluded media directories ignored.

### Task 2: Verify the snapshot

**Files:**
- Test: `tests/*.py`
- Test: `site/assets/app.js`

**Interfaces:**
- Consumes: curated working tree
- Produces: fresh test and safety evidence

- [ ] **Step 1: Run Python tests**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: 68 tests pass with zero failures.

- [ ] **Step 2: Check browser application syntax**

Run:

```bash
node --check site/assets/app.js
```

Expected: exit code 0.

- [ ] **Step 3: Scan the staged snapshot**

List staged paths over 10 MB and search staged text for credential-shaped values.
Expected: no oversized files and no secrets.

### Task 3: Publish and verify

**Files:**
- No additional files

**Interfaces:**
- Consumes: verified `main` commit
- Produces: public GitHub repository

- [ ] **Step 1: Initialize and connect Git**

Run:

```bash
git init -b main
git remote add origin https://github.com/poommmes-del/cours-d-arabe.git
```

Expected: local `main` tracks the requested empty repository after push.

- [ ] **Step 2: Commit curated files**

Stage explicit source paths and commit with message
`docs: publish Cours d'Arabe source`.

- [ ] **Step 3: Push and verify**

Run:

```bash
git push -u origin main
gh repo view poommmes-del/cours-d-arabe --web=false
```

Expected: public repository has `main` as default branch and renders `README.md`.
