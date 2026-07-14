# Three Priority Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger course de transcription, écrasement du manifeste lors des exécutions partielles et test CSS obsolète, sans modifier données métier.

**Architecture:** Frontend protège mutations DOM par génération monotone. Pipeline calcule état final du manifeste avant sérialisation atomique. Test CSS vérifie seuil fonctionnel plutôt que valeur exacte.

**Tech Stack:** JavaScript navigateur, Playwright, Python 3 `unittest`, TSV via `csv`.

## Global Constraints

- Usage local personnel.
- Aucun nouveau paquet ou format de données.
- Aucun appel réseau, API Deepgram, téléchargement ou réencodage pendant tests unitaires.
- `site/data/catalog.json`, `audios-opus/manifest.tsv`, audios, transcriptions et PDF restent inchangés.
- Toute commande shell est préfixée par `rtk`.
- Projet sans dépôt Git : étapes de commit remplacées par lecture ciblée des sources et résultats de tests.

---

### Task 1: Corriger contrat CSS obsolète

**Files:**
- Modify: `tests/test_site_data.py:440-448`
- Test: `tests/test_site_data.py`

**Interfaces:**
- Consumes: règles CSS `.markdown-body` et `.transcript-text`.
- Produces: assertions de taille minimale en pixels.

- [x] **Step 0: Capturer empreintes données avant premier edit**

Run:

```bash
rtk proxy sha256sum audios-opus/manifest.tsv site/data/catalog.json
```

Expected: deux hashes conservés dans sortie de session pour comparaison finale.

- [x] **Step 1: Vérifier test rouge existant**

Run:

```bash
rtk test python3 -m unittest tests.test_site_data.SiteDataTest.test_beginner_reading_uses_larger_arabic_font_and_harakat -v
```

Expected: FAIL, `font-size: 23px;` absent car CSS vaut `28px`.

- [x] **Step 2: Remplacer égalité textuelle par extraction numérique**

```python
        markdown_size = re.search(r"font-size:\s*([0-9]+(?:\.[0-9]+)?)px", markdown_block.group("body"))
        transcript_size = re.search(r"font-size:\s*([0-9]+(?:\.[0-9]+)?)px", transcript_block.group("body"))

        self.assertIsNotNone(markdown_size)
        self.assertIsNotNone(transcript_size)
        self.assertGreaterEqual(float(markdown_size.group(1)), 23)
        self.assertGreaterEqual(float(transcript_size.group(1)), 22)
```

Supprimer deux anciens `assertIn` exacts. Ne pas modifier `site/assets/app.css`.

- [x] **Step 3: Vérifier test vert**

Run:

```bash
rtk test python3 -m unittest tests.test_site_data.SiteDataTest.test_beginner_reading_uses_larger_arabic_font_and_harakat -v
```

Expected: PASS.

- [x] **Step 4: Inspecter changement**

Run:

```bash
rtk read tests/test_site_data.py
```

Expected: seules assertions CSS changent.

---

### Task 2: Empêcher réponse transcription obsolète

**Files:**
- Create: `tests/ui_transcript_race.spec.js`
- Modify: `site/assets/app.js:3-14`
- Modify: `site/assets/app.js:447-459`
- Modify: `README.md:581`

**Interfaces:**
- Consumes: `state`, `loadAndRenderTranscript(lesson)`, `getTranscript(lesson)`.
- Produces: `state.transcriptRenderVersion: number`; seuls résultats génération courante modifient DOM.

- [x] **Step 1: Écrire test Playwright rouge**

```javascript
const { test, expect } = require("@playwright/test");

test("latest transcript response wins", async ({ page }) => {
  let requestNumber = 0;
  let releaseFirst = () => {};
  let markFirstStarted = () => {};
  let markFirstFinished = () => {};
  const firstGate = new Promise((resolve) => {
    releaseFirst = resolve;
  });
  const firstStarted = new Promise((resolve) => {
    markFirstStarted = resolve;
  });
  const firstFinished = new Promise((resolve) => {
    markFirstFinished = resolve;
  });

  await page.route("**/transcriptions-deepgram/**", async (route) => {
    const current = ++requestNumber;
    if (current === 1) {
      markFirstStarted();
      await firstGate;
    }
    await route.fulfill({
      status: 200,
      contentType: "text/markdown; charset=utf-8",
      body: `## Transcription\n\n${current === 1 ? "FIRST_RESPONSE" : "SECOND_RESPONSE"}\n\n## Segments\n`,
    });
    if (current === 1) {
      markFirstFinished();
    }
  });

  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator(".course-tile").first().click();
  await firstStarted;
  await page.locator("#lessonSelect").selectOption({ index: 1 });
  await expect(page.locator("#transcriptText")).toHaveText("SECOND_RESPONSE");

  releaseFirst();
  await firstFinished;
  await expect(page.locator("#transcriptText")).toHaveText("SECOND_RESPONSE");
});
```

- [x] **Step 2: Lancer serveur loopback et vérifier test rouge**

Terminal serveur:

```bash
rtk proxy python3 -m http.server 8766 --bind 127.0.0.1
```

Terminal test:

```bash
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_transcript_race.spec.js --browser=chromium --reporter=line --output=/tmp/cours-arabe-race-red'
```

Expected: FAIL final, `#transcriptText` vaut `FIRST_RESPONSE`.

- [x] **Step 3: Ajouter génération monotone**

Dans `state`:

```javascript
  transcriptRenderVersion: 0,
```

Remplacer `loadAndRenderTranscript`:

```javascript
async function loadAndRenderTranscript(lesson) {
  const renderVersion = ++state.transcriptRenderVersion;
  els.transcriptText.textContent = "Chargement...";
  els.segmentList.innerHTML = "";
  try {
    const markdown = await getTranscript(lesson);
    if (renderVersion !== state.transcriptRenderVersion) {
      return;
    }
    const transcript = extractTranscript(markdown);
    const segments = extractSegments(markdown);
    els.transcriptText.innerHTML = highlight(applyHarakat(transcript || "Transcription vide."), state.query);
    renderSegments(segments);
  } catch (error) {
    if (renderVersion !== state.transcriptRenderVersion) {
      return;
    }
    els.transcriptText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
    els.segmentList.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}
```

- [x] **Step 4: Vérifier test vert**

Run:

```bash
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_transcript_race.spec.js --browser=chromium --reporter=line --output=/tmp/cours-arabe-race-green'
```

Expected: 1 passed.

- [x] **Step 5: Ajouter spec à commande README**

Ajouter `tests/ui_transcript_race.spec.js` après deux specs existantes dans commande Playwright de `README.md`.

- [x] **Step 6: Vérifier syntaxe et diff**

Run:

```bash
rtk proxy node --check site/assets/app.js
rtk proxy node --check tests/ui_transcript_race.spec.js
rtk read site/assets/app.js
rtk read tests/ui_transcript_race.spec.js
rtk rg -n 'ui_transcript_race' README.md
```

Expected: checks passent; aucun changement hors compteur, garde obsolescence, nouvelle spec et commande docs.

---

### Task 3: Préserver manifeste pendant exécution partielle

**Files:**
- Create: `tests/test_archive_audio_compress.py`
- Modify: `outils/archive_audio_compress.py:189-247`

**Interfaces:**
- Consumes: `ManifestRow = tuple[AudioJob, Path, int]`.
- Produces:
  - `read_manifest(path: Path) -> list[ManifestRow]`
  - `merge_manifest_rows(existing, updates, *, replace_all, replace_identifiers) -> list[ManifestRow]`
  - `write_manifest(path: Path, rows: list[ManifestRow]) -> None`, atomique.

- [x] **Step 1: Écrire tests rouges**

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from outils.archive_audio_compress import (
    AudioJob,
    merge_manifest_rows,
    read_manifest,
    write_manifest,
)


def manifest_row(identifier: str, name: str, size: int):
    job = AudioJob(identifier, name, 60.0, 1000, f"https://example.test/{name}")
    return job, Path(f"audios-opus/{identifier}/{name}.opus"), size


class ManifestMergeTest(unittest.TestCase):
    def as_map(self, rows):
        return {(job.identifier, job.name): size for job, _path, size in rows}

    def test_limit_updates_only_processed_keys(self):
        existing = [
            manifest_row("a", "1.mp3", 10),
            manifest_row("a", "2.mp3", 20),
            manifest_row("b", "1.mp3", 30),
        ]
        updates = [manifest_row("a", "1.mp3", 99)]

        merged = merge_manifest_rows(
            existing,
            updates,
            replace_all=False,
            replace_identifiers=set(),
        )

        self.assertEqual(
            {("a", "1.mp3"): 99, ("a", "2.mp3"): 20, ("b", "1.mp3"): 30},
            self.as_map(merged),
        )

    def test_identifier_replaces_only_target_course(self):
        existing = [
            manifest_row("a", "old.mp3", 10),
            manifest_row("a", "stale.mp3", 20),
            manifest_row("b", "1.mp3", 30),
        ]
        updates = [manifest_row("a", "new.mp3", 99)]

        merged = merge_manifest_rows(
            existing,
            updates,
            replace_all=False,
            replace_identifiers={"a"},
        )

        self.assertEqual(
            {("a", "new.mp3"): 99, ("b", "1.mp3"): 30},
            self.as_map(merged),
        )

    def test_full_run_replaces_everything(self):
        merged = merge_manifest_rows(
            [manifest_row("old", "1.mp3", 10)],
            [manifest_row("new", "1.mp3", 20)],
            replace_all=True,
            replace_identifiers=set(),
        )
        self.assertEqual({("new", "1.mp3"): 20}, self.as_map(merged))

    def test_manifest_round_trip_is_sorted(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.tsv"
            write_manifest(
                path,
                [
                    manifest_row("b", "10.mp3", 10),
                    manifest_row("a", "2.mp3", 20),
                    manifest_row("a", "1.mp3", 30),
                ],
            )

            rows = read_manifest(path)
            self.assertEqual(
                [("a", "1.mp3"), ("a", "2.mp3"), ("b", "10.mp3")],
                [(job.identifier, job.name) for job, _path, _size in rows],
            )
            self.assertEqual([], list(path.parent.glob(f".{path.name}.*.tmp")))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Vérifier tests rouges**

Run:

```bash
rtk test python3 -m unittest tests.test_archive_audio_compress -v
```

Expected: ERROR import, `merge_manifest_rows` et `read_manifest` absents.

- [x] **Step 3: Ajouter lecture, fusion et écriture atomique**

Ajouter après `encode_one`:

```python
ManifestRow = tuple[AudioJob, Path, int]
MANIFEST_FIELDS = [
    "identifier",
    "name",
    "length_seconds",
    "source_size_bytes",
    "compressed_size_bytes",
    "path",
]


def read_manifest(manifest: Path) -> list[ManifestRow]:
    if not manifest.exists():
        return []
    rows: list[ManifestRow] = []
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            job = AudioJob(
                identifier=row["identifier"],
                name=row["name"],
                length_seconds=float(row["length_seconds"]),
                size_bytes=int(row["source_size_bytes"]),
                url="",
            )
            rows.append((job, Path(row["path"]), int(row["compressed_size_bytes"])))
    return rows


def merge_manifest_rows(
    existing: list[ManifestRow],
    updates: list[ManifestRow],
    *,
    replace_all: bool,
    replace_identifiers: set[str],
) -> list[ManifestRow]:
    merged: dict[tuple[str, str], ManifestRow] = {}
    if not replace_all:
        for row in existing:
            job, _path, _size = row
            if job.identifier not in replace_identifiers:
                merged[(job.identifier, job.name)] = row
    for row in updates:
        job, _path, _size = row
        merged[(job.identifier, job.name)] = row
    return list(merged.values())
```

Remplacer `write_manifest`:

```python
def write_manifest(manifest: Path, rows: list[ManifestRow]) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest.with_name(f".{manifest.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(MANIFEST_FIELDS)
            for job, path, size in sorted(
                rows,
                key=lambda row: (row[0].identifier, natural_key(row[0].name)),
            ):
                writer.writerow(
                    [
                        job.identifier,
                        job.name,
                        job.length_seconds,
                        job.size_bytes,
                        size,
                        path,
                    ]
                )
        os.replace(temporary, manifest)
    finally:
        if temporary.exists():
            temporary.unlink()
```

- [x] **Step 4: Brancher politique complète/identifiant/limite**

Remplacer filtre `--limit`:

```python
    if args.limit is not None:
        jobs = jobs[: args.limit]
```

Puis remplacer appel final:

```python
    manifest = args.out_dir / "manifest.tsv"
    existing_rows = read_manifest(manifest)
    replace_all = not args.identifier and args.limit is None
    replace_identifiers = set(args.identifier) if args.identifier and args.limit is None else set()
    manifest_rows = merge_manifest_rows(
        existing_rows,
        rows,
        replace_all=replace_all,
        replace_identifiers=replace_identifiers,
    )
    write_manifest(manifest, manifest_rows)
```

Conserver calcul `compressed_size` sur `rows` : il décrit exécution courante.

- [x] **Step 5: Vérifier tests verts**

Run:

```bash
rtk test python3 -m unittest tests.test_archive_audio_compress -v
```

Expected: 4 tests pass.

- [x] **Step 6: Vérifier syntaxe et diff**

Run:

```bash
rtk proxy python3 -m py_compile outils/archive_audio_compress.py tests/test_archive_audio_compress.py
rtk read outils/archive_audio_compress.py
rtk read tests/test_archive_audio_compress.py
```

Expected: syntaxe valide; aucun appel FFmpeg/réseau dans tests.

---

### Task 4: Vérification intégrée

**Files:**
- Verify only: tous fichiers projet.

**Interfaces:**
- Consumes: trois corrections précédentes.
- Produces: preuves tests, données inchangées, serveur arrêté.

- [x] **Step 1: Lancer suite Python complète**

```bash
rtk test python3 -m unittest discover -v
```

Expected: tous tests passent, zéro failure/error.

- [x] **Step 2: Lancer checks syntaxe**

```bash
rtk proxy python3 -m py_compile outils/archive_audio_compress.py outils/generate_site_data.py outils/generate_pedagogical_courses.py outils/deepgram_archive.py outils/shamela_download.py
rtk proxy node --check site/assets/app.js
rtk proxy node --check tests/ui_quiz.spec.js
rtk proxy node --check tests/ui_resources.spec.js
rtk proxy node --check tests/ui_transcript_race.spec.js
rtk proxy bash -n ouvrir-site.sh
```

Expected: sorties vides, codes 0.

- [x] **Step 3: Lancer trois tests Playwright**

Avec serveur loopback actif:

```bash
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_quiz.spec.js tests/ui_resources.spec.js tests/ui_transcript_race.spec.js --browser=chromium --reporter=line --output=/tmp/cours-arabe-final-results'
```

Expected: 3 passed.

- [x] **Step 4: Vérifier catalogue déterministe sans écriture**

```bash
rtk proxy python3 -c 'import json; from pathlib import Path; from outils.generate_site_data import build_catalog; old=json.loads(Path("site/data/catalog.json").read_text(encoding="utf-8")); new=build_catalog(); print({"equal": old == new, "courses": new["course_count"], "lessons": new["lesson_count"]})'
```

Expected: `{'equal': True, 'courses': 14, 'lessons': 792}`.

- [x] **Step 5: Vérifier données non modifiées et arrêter serveur**

```bash
rtk proxy sha256sum audios-opus/manifest.tsv site/data/catalog.json
rtk proxy curl -sS --max-time 1 http://127.0.0.1:8766/site/
```

Comparer hashes avant/après exécution. Après arrêt serveur, `curl` doit échouer avec code 7.

- [x] **Step 6: Revue finale**

Relire sources des six fichiers autorisés :

- `tests/test_site_data.py`
- `tests/ui_transcript_race.spec.js`
- `site/assets/app.js`
- `README.md`
- `tests/test_archive_audio_compress.py`
- `outils/archive_audio_compress.py`

Confirmer aucune modification audio, transcription, PDF, catalogue ou manifest courant.
