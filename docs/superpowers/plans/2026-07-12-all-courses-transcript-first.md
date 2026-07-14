# All Courses Transcript-First Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development and superpowers:dispatching-parallel-agents to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remplacer les treize cours restants par des parcours arabes transcript-first complets, produits par vagues de trois cours et publies sans checkpoint humain.

**Architecture:** Une fondation schema v2 generalise le builder Ajroumiya et une configuration verrouille ordre, vagues et plages de modules. Trois agents durables produisent chacun un cours dans des fichiers disjoints; le controleur assemble et regenere le catalogue une fois par vague, puis verifie tests, navigateur et empreintes avant de continuer.

**Tech Stack:** Python 3 standard library, unittest, Markdown, JSON, Playwright Chromium, shell RTK.

## Global Constraints

- Ordre public exact : `moutammima`, `qatr-nada`, `qawaid-i3raab-sa3di`, `qawaid-i3raab-zawawi`, `mawsil-toullab`, `shoudhour-dhahab`, `alfiya-nahw`, `moulakhas-sarfi`, `nadhm-maqsoud`, `alfiya-sarf`, `laamiya-af3al`, `dourous-balagha`, `maani-we-bayan`.
- Vagues exactes : cours 1-3, 4-6, 7-9, 10-12, puis 13.
- Langue cours/questionnaires : arabe uniquement.
- Chaque module : treize sections Ajroumiya dans ordre exact et 8 a 10 questions raisonnees.
- Couverture : chaque lecon possede audio_span ou exclusion motivee.
- Aucune provenance interne dans contenu public.
- Aucun reseau, telechargement, API, transcription ou reencodage.
- Audios, transcriptions, PDF, Shamela et manifest audio immuables.
- Cours hors vague et cours deja publies immuables.
- Catalogue final et intermediaire : 14 cours, 792 lecons.
- Projet non-Git : aucun commit, branche ou worktree; rapports et ledgers font foi.
- Toutes commandes shell prefixees `rtk`.
- Edits manuels via `apply_patch` uniquement.
- Aucun checkpoint utilisateur; tout echec est corrige automatiquement dans le perimetre approuve.

## File Structure

- Modify: `outils/build_pedagogical_course.py` - schema v2 multi-cours.
- Create: `outils/manage_course_waves.py` - configuration, baselines, statut et verification de vagues.
- Create: `cours-pedagogiques/course-build-config.json` - ordre, vagues, plages de modules.
- Modify: `tests/test_ajroumiya_pedagogy.py` - migration schema v2 sans regression.
- Create: `tests/test_course_wave_manager.py` - tests configuration/baselines/vagues.
- Create: `tests/ui_course_quality.spec.js` - parcours navigateur parametrable par cours.
- Modify: `README.md` - commandes multi-cours.
- Create per course: `cours-pedagogiques/<id>/source-map.json`, `modules/*.md`, `cours.before-transcript-first.md`.
- Modify per course: `cours-pedagogiques/<id>/cours.md`.
- Create per course: `.superpowers/sdd/all-courses/<id>/*`.
- Create: `.superpowers/sdd/all-courses/progress.md`, `wave-1-report.md` a `wave-5-report.md`, `global-final-review.md`.

---

### Task 1: Generaliser builder au schema v2

**Files:**
- Modify: `outils/build_pedagogical_course.py`
- Modify: `tests/test_ajroumiya_pedagogy.py`
- Modify: `cours-pedagogiques/ajroumiya/source-map.json`
- Report: `.superpowers/sdd/all-courses/task-1-report.md`

**Interfaces:**
- Produces: `module_count_range(data: dict[str, Any]) -> tuple[int, int]`.
- Changes: `validate_source_batch(..., course_id: str)` validates dynamic identifier.
- Changes: `validate_source_map(..., expected_identifier: str)` validates schema 2 and generic references.
- Preserves: existing CLI options and Ajroumiya public output.

- [ ] Write failing tests proving non-Ajroumiya `course_id` accepted when equal to identifier, mismatches rejected, custom `[30,55]` accepted, out-of-range fragments rejected, empty canonical refs allowed only when source inventory declares absence.
- [ ] Run `rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy -v`; expected RED on hardcoded `ajroumiya` and 25-35 range.
- [ ] Implement schema 2: require `module_count_range`, `canonical_refs`, `supporting_refs`, and `source_inventory.canonical_available` boolean; require canonical refs when true and allow empty only when false; compare identifiers dynamically.
- [ ] Migrate Ajroumiya source-map to schema 2 with `[25,35]`, existing matn refs as canonical, charh refs as supporting, same 35 modules/spans/statuses.
- [ ] Run Ajroumiya validate-only, targeted tests and full Python suite; expected all green and `source-map valid modules=35 lessons=30`.
- [ ] Record pre/post Ajroumiya `cours.md` and catalog object hashes; expected unchanged.

### Task 2: Ajouter gestionnaire durable de vagues

**Files:**
- Create: `cours-pedagogiques/course-build-config.json`
- Create: `outils/manage_course_waves.py`
- Create: `tests/test_course_wave_manager.py`
- Create: `tests/ui_course_quality.spec.js`
- Create: `.superpowers/sdd/all-courses/progress.md`
- Report: `.superpowers/sdd/all-courses/task-2-report.md`

**Interfaces:**
- `load_config(path: Path) -> list[CourseBuildConfig]`.
- `capture_baseline(root: Path, identifiers: list[str], output: Path) -> None`.
- `verify_wave(root: Path, wave: int, baseline: Path) -> list[str]` returns deterministic errors.
- CLI: `--init`, `--status`, `--verify-wave N`.

- [ ] Write RED tests for unique order 1-13, waves `[[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13]]`, exact lesson counts, valid module ranges and hash drift detection outside active wave.
- [ ] Create config with ranges: `moutammima/qatr-nada/qawaid-i3raab-sa3di` `[30,55]`; `qawaid-i3raab-zawawi` `[25,40]`; `mawsil-toullab/shoudhour-dhahab` `[30,55]`; `alfiya-nahw` `[70,110]`; `moulakhas-sarfi/nadhm-maqsoud` `[30,55]`; `alfiya-sarf` `[25,40]`; `laamiya-af3al/dourous-balagha` `[30,55]`; `maani-we-bayan` `[25,40]`.
- [ ] Implement baseline hashes for manifest, audio file metadata, transcriptions, PDF, Shamela, Ajroumiya public object and every course object outside active wave.
- [ ] Initialize durable ledger with foundation/waves pending and per-course batch checkpoints.
- [ ] Write generic Playwright test using `COURSE_IDS=id1,id2,id3`; for each selected course open first/middle/last module, assert required headings, 8-10 questions and visible answer toggle. Without variable, select all 14 courses.
- [ ] Run Playwright against Ajroumiya as RED/GREEN compatibility check; expected one course and three sampled modules pass.
- [ ] Run new tests plus full Python suite; expected green.

### Task 3: Inventorier vague 1 en parallele

**Files:**
- Create under `.superpowers/sdd/all-courses/moutammima/`
- Create under `.superpowers/sdd/all-courses/qatr-nada/`
- Create under `.superpowers/sdd/all-courses/qawaid-i3raab-sa3di/`

**Interfaces:** Each agent produces `baseline.json`, `source-inventory.md`, `progress.md` and source batches conforming schema.

- [ ] Dispatch three agents, one per course, with write scopes disjoints.
- [ ] Process exact batches: Moutammima `1:15,16:30,31:45,46:59`; Qatr `1:15,16:30,31:45,46:60,61:69`; Sa3di `1:15,16:30,31:44`.
- [ ] For every audio, record teaching/example/student_question/repetition/administrative spans, claims, examples and uncertainties.
- [ ] Inventory all local canonical/supporting sources; document explicit absence instead of fake path.
- [ ] Validate every batch with generic builder and mark checkpoint complete only after code 0.

### Task 4: Architecturer et rediger vague 1

**Files:**
- Create: `cours-pedagogiques/moutammima/source-map.json`, `modules/*.md`
- Create: `cours-pedagogiques/qatr-nada/source-map.json`, `modules/*.md`
- Create: `cours-pedagogiques/qawaid-i3raab-sa3di/source-map.json`, `modules/*.md`
- Reports: per-course architecture, writing shards and final report.

- [ ] Each course agent synthesizes semantic source-map within `[30,55]`, covers all lessons/exclusions, statuses pending except transcript verified.
- [ ] Validate each source-map `--allow-pending --source-map-only`.
- [ ] Each agent writes modules in contiguous shards of at most 10 files; after each shard run fragment validation and update ledger.
- [ ] Set grammar/arabic/pedagogy verified only after all fragments pass source checks and questionnaire contract.
- [ ] Run `--validate-only` per course; expected code 0 and no pending.

### Task 5: Integrer vague 1

**Files:**
- Create once: three `cours.before-transcript-first.md`
- Modify: three `cours.md`, `site/data/catalog.json`
- Create: `.superpowers/sdd/all-courses/wave-1-report.md`

- [ ] Capture active-wave baseline and protected hashes.
- [ ] Build three courses in catalogue order; verify backups match pre-wave course hashes.
- [ ] Regenerate catalog once; expect 14/792.
- [ ] Run full Python suite and `tests/ui_course_quality.spec.js` for three identifiers.
- [ ] Run `manage_course_waves.py --verify-wave 1`; expected zero errors, no drift outside wave.
- [ ] Dispatch independent wave audit; fix complete Critical/Important list with one correction agent, rebuild and re-run until zero.
- [ ] Mark wave 1 and three course ledgers complete.

### Task 6: Produire vague 2 en parallele

**Files:**
- Course ids: `qawaid-i3raab-zawawi`, `mawsil-toullab`, `shoudhour-dhahab`.
- Create corresponding source maps, modules, SDD artifacts, backups and wave report.

- [ ] Dispatch three disjoint course agents.
- [ ] Process batches: Zawawi `1:15,16:30,31:37`; Mawsil `1:15,16:30,31:45,46:48`; Shoudhour `1:15,16:30,31:45,46:60,61:75,76:76`.
- [ ] Each agent inventories local canonical/supporting sources, records baseline, extracts every listed audio batch and validates it code 0.
- [ ] Each agent builds semantic source-map covering every lesson or exclusion, then validates pending architecture.
- [ ] Each agent writes contiguous module shards of at most 10, validates after every shard, consolidates four statuses to verified, then runs validate-only code 0.
- [ ] Build three courses in order, regenerate catalog once, verify backups, Python, browser and `--verify-wave 2`.
- [ ] Run independent wave audit/fix loop to zero Critical/Important.
- [ ] Mark wave 2 complete.

### Task 7: Produire vague 3 en parallele

**Files:**
- Course ids: `alfiya-nahw`, `moulakhas-sarfi`, `nadhm-maqsoud`.
- Create corresponding source maps, modules, SDD artifacts, backups and wave report.

- [ ] Dispatch three disjoint course agents; Alfiya agent checkpoints every batch to survive long context.
- [ ] Process Alfiya batches `1:15,16:30,31:45,46:60,61:75,76:90,91:105,106:120,121:135,136:150,151:163`.
- [ ] Process Moulakhas `1:15,16:30,31:43`; Nadhm `1:15,16:30,31:45,46:60`.
- [ ] Each agent inventories sources and baseline, validates every audio batch, creates semantic source-map with complete lesson coverage, writes module shards <=10, verifies all statuses and obtains validate-only code 0; Alfiya range `[70,110]`, others `[30,55]`.
- [ ] Build three courses in order, regenerate catalog once, verify backups, Python, browser and `--verify-wave 3`.
- [ ] Run independent wave audit/fix loop to zero Critical/Important.
- [ ] Mark wave 3 complete.

### Task 8: Produire vague 4 en parallele

**Files:**
- Course ids: `alfiya-sarf`, `laamiya-af3al`, `dourous-balagha`.
- Create corresponding source maps, modules, SDD artifacts, backups and wave report.

- [ ] Dispatch three disjoint course agents.
- [ ] Process Alfiya Sarf `1:15,16:30,31:32`; Laamiya `1:15,16:30,31:41`; Dourous `1:15,16:30,31:45,46:60`.
- [ ] Use sarf answer rubric for first two and balagha rubric for Dourous.
- [ ] Each agent inventories sources and baseline, validates every audio batch, creates semantic source-map with complete lesson coverage, writes module shards <=10 using correct sarf/balagha rubric, verifies all statuses and obtains validate-only code 0.
- [ ] Build three courses in order, regenerate catalog once, verify backups, Python, browser and `--verify-wave 4`.
- [ ] Run independent wave audit/fix loop to zero Critical/Important.
- [ ] Mark wave 4 complete.

### Task 9: Produire vague 5

**Files:**
- Course id: `maani-we-bayan`.
- Create source-map, modules, SDD artifacts, backup and wave report.

- [ ] Dispatch one course agent; process `1:15,16:30`.
- [ ] Apply balagha rubric and module range `[25,40]`.
- [ ] Agent inventories sources and baseline, validates both audio batches, creates semantic source-map covering 30 lecons, writes module shards <=10 with balagha rubric, verifies all statuses and obtains validate-only code 0.
- [ ] Build course, regenerate catalog once, verify backup, Python, browser and `--verify-wave 5`.
- [ ] Run independent final-course audit/fix loop to zero Critical/Important.
- [ ] Mark wave 5 complete.

### Task 10: Documentation et verification navigateur globale

**Files:**
- Verify: `tests/ui_course_quality.spec.js`
- Modify: `README.md`
- Test: all JS/Python syntax and Playwright.

**Interfaces:** `COURSE_IDS=id1,id2,id3` selects exact courses; absent value selects all 14.

- [ ] Document generic builder, wave manager, validation and Playwright commands.
- [ ] Verify environment parsing `COURSE_IDS` and deterministic selectors against one course then all 14, without changing site UI.
- [ ] Run syntax checks, Python suite and Playwright all 14 courses; expected green.
- [ ] Stop server; confirm curl code 7 and no listener.

### Task 11: Integrite et cloture globale

**Files:**
- Create: `.superpowers/sdd/all-courses/global-final-review.md`
- Modify: `.superpowers/sdd/all-courses/progress.md`
- Verify: all course/source/protected artifacts.

- [ ] Verify 13 backups exist and equal recorded pre-wave hashes.
- [ ] Verify every source-map covers exact catalog lesson IDs and has all statuses verified.
- [ ] Verify every course module count within configured range and every questionnaire 8-10.
- [ ] Verify catalog reproducibility, 14 courses, 792 lessons and exact course order.
- [ ] Verify manifest, audios, transcriptions, PDF and Shamela hashes against foundation baseline.
- [ ] Run fresh Python, syntax and browser suites.
- [ ] Dispatch senior global auditor; fix all Critical/Important in one wave, rebuild and re-run until approved.
- [ ] Mark foundation, five waves and thirteen course ledgers complete; leave no server process.

## Execution Policy

User selected three-course parallel execution and waived all human review gates. Start Task 1 immediately. Between tasks, continue automatically unless blocked by missing local source, repeated validation failure or conflicting filesystem edits. Use durable reports instead of conversational checkpoints.
