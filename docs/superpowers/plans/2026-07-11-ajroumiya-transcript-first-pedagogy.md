# Ajroumiya Transcript-First Pedagogy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) to implement this plan task-by-task. Use superpowers:dispatching-parallel-agents only for the explicitly independent source, writing, and review waves. Steps use checkbox syntax for tracking.

**Goal:** Remplacer le parcours Ajroumiya par 25 à 35 modules arabes extrêmement pédagogiques, fondés sur les 30 transcriptions audio, validés par le matn et les charh, avec 8 à 10 questions raisonnées par module.

**Architecture:** Trois dossiers sources couvrent les audios 1–10, 11–20 et 21–30. Une cartographie interne relie chaque module aux plages audio et aux sources canoniques; des fragments Markdown disjoints sont validés puis assemblés atomiquement vers cours.md. Le site continue de consommer le format existant.

**Tech Stack:** Python 3 standard library, unittest, Markdown, JSON, JavaScript navigateur, Playwright Chromium.

## Global Constraints

- Périmètre strict : ajroumiya uniquement; les treize autres cours restent inchangés.
- Langue du cours et des questionnaires : arabe uniquement.
- Nombre final : 25 à 35 titres H2, sans module Accueil implicite.
- Chaque module : 15 à 25 minutes d’apprentissage et toutes les sections pédagogiques de la spécification.
- Chaque questionnaire : 8 à 10 questions explicites avec réponses raisonnées; aucun fallback générique.
- Audio et transcription fixent ordre, portée, explications et exemples; matn fixe formulation canonique; charh complète seulement.
- Provenance, minutages et références restent dans source-map.json et ne sont jamais affichés.
- Aucun réseau, téléchargement, appel API, nouvelle transcription ou réencodage.
- Audios, transcriptions, PDF, exports Shamela et audios-opus/manifest.tsv restent inchangés.
- Catalogue final : 14 cours et 792 leçons.
- Aucun autre objet de cours du catalogue ne change.
- Projet non-Git : aucun commit, branche ou worktree. Chaque tâche produit rapport et revue dans .superpowers/sdd/ajroumiya/.
- Toutes commandes shell sont préfixées par rtk.
- CodeGraph précède toute lecture structurelle; recherches littérales utilisent rg.
- Édits de fichiers via apply_patch uniquement.

## Structure de fichiers verrouillée

### Créés

- outils/build_pedagogical_course.py — validation, sauvegarde et assemblage atomique.
- tests/test_ajroumiya_pedagogy.py — tests unitaires du builder et contrat final.
- tests/ui_ajroumiya_course.spec.js — parcours navigateur début/milieu/fin.
- cours-pedagogiques/ajroumiya/source-map.json — provenance interne finale.
- cours-pedagogiques/ajroumiya/modules/ — un module par fichier, nommé par index à deux chiffres puis slug arabe du titre; exemple 01-منزلة-الآجرومية.md.
- cours-pedagogiques/ajroumiya/cours.before-transcript-first.md — sauvegarde immuable.
- .superpowers/sdd/ajroumiya/source-01-10.json — dossier source audios 1–10.
- .superpowers/sdd/ajroumiya/source-11-20.json — dossier source audios 11–20.
- .superpowers/sdd/ajroumiya/source-21-30.json — dossier source audios 21–30.
- .superpowers/sdd/ajroumiya/progress.md — ledger durable.

### Modifiés

- cours-pedagogiques/ajroumiya/cours.md — assemblage final uniquement.
- site/data/catalog.json — nouveaux modules/questions Ajroumiya.
- README.md — commandes auteur et test navigateur.

### Interfaces communes

ModuleFragment possède order: int, path: Path, title: str, text: str et question_count: int.

- load_fragments(modules_dir: Path) -> list[ModuleFragment]
- validate_fragment(path: Path, order: int) -> ModuleFragment
- assemble_fragments(fragments: list[ModuleFragment], enforce_count: bool = True) -> str
- load_lesson_durations(catalog_path: Path, identifier: str) -> dict[str, float]
- validate_source_batch(data: dict[str, Any], durations: dict[str, float], expected_ids: list[str]) -> None
- validate_source_map(data: dict[str, Any], fragments: list[ModuleFragment], durations: dict[str, float], root: Path, require_verified: bool, require_fragments: bool) -> None
- expected_module_id(identifier: str, index: int, title: str) -> str
- write_course(root: Path, identifier: str, content: str) -> Path

Toutes fonctions lèvent PedagogyValidationError avec une liste déterministe de messages en cas d’échec.

---

### Task 1: Validateur et assembleur de fragments

**Files:**
- Create: outils/build_pedagogical_course.py
- Create: tests/test_ajroumiya_pedagogy.py
- Report: .superpowers/sdd/ajroumiya/task-1-report.md

**Interfaces:**
- Consumes: fragments Markdown commençant par un seul titre H2.
- Produces: ModuleFragment, validate_fragment(), load_fragments(), assemble_fragments().

- [x] **Step 1: Écrire tests rouges du contrat de fragment**

Créer ce squelette de test et compléter les huit questions via la boucle montrée :

~~~python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from outils.build_pedagogical_course import (
    PedagogyValidationError,
    assemble_fragments,
    load_fragments,
    validate_fragment,
)


REQUIRED = [
    "الهدف",
    "قبل أن تبدأ",
    "شرح المسألة",
    "القاعدة",
    "لماذا؟",
    "أمثلة متدرجة",
    "تحليل خطوة خطوة",
    "خطأ شائع",
    "تدريب موجه",
    "تدريب مستقل",
    "خلاصة للحفظ",
    "تشخيص قبلي",
]


def valid_text(title: str = "منزلة الآجرومية") -> str:
    sections = "\n\n".join(f"### {name}\n\nمحتوى عربي واضح." for name in REQUIRED)
    questions = "\n\n".join(
        f"{index}. سؤال تطبيقي رقم {index}؟\n- الجواب: جواب صحيح مع بيان السبب."
        for index in range(1, 9)
    )
    return f"## {title}\n\n{sections}\n\n### أسئلة التحقق\n\n{questions}\n"


class FragmentValidationTest(unittest.TestCase):
    def test_valid_fragment_parses_eight_questions(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            path.write_text(valid_text(), encoding="utf-8")
            fragment = validate_fragment(path, 1)
            self.assertEqual(1, fragment.order)
            self.assertEqual("منزلة الآجرومية", fragment.title)
            self.assertEqual(8, fragment.question_count)

    def test_fragment_rejects_missing_section(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            path.write_text(valid_text().replace("### لماذا؟", "### تفسير"), encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "لماذا؟"):
                validate_fragment(path, 1)

    def test_fragment_rejects_five_questions(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            text = valid_text()
            text = text[: text.index("6. سؤال تطبيقي")]
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "8 إلى 10"):
                validate_fragment(path, 1)

    def test_fragment_rejects_empty_section(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-منزلة-الآجرومية.md"
            text = valid_text().replace("### القاعدة\n\nمحتوى عربي واضح.", "### القاعدة\n")
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(PedagogyValidationError, "section vide القاعدة"):
                validate_fragment(path, 1)

    def test_fragments_assemble_in_numeric_order(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "02-الوحدة-الثانية.md").write_text(valid_text("الوحدة الثانية").replace("تشخيص قبلي", "مراجعة تراكمية"), encoding="utf-8")
            (directory / "01-الوحدة-الأولى.md").write_text(valid_text("الوحدة الأولى"), encoding="utf-8")
            result = assemble_fragments(load_fragments(directory), enforce_count=False)
            self.assertLess(result.index("الوحدة الأولى"), result.index("الوحدة الثانية"))
~~~

- [x] **Step 2: Vérifier RED**

Run:

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy.FragmentValidationTest -v
~~~

Expected: import error, outils.build_pedagogical_course absent.

- [x] **Step 3: Implémenter contrat minimal**

Créer outils/build_pedagogical_course.py avec ces constantes et comportements :

~~~python
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from outils.generate_site_data import parse_questions, slug


ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "cours-pedagogiques"
CATALOG = ROOT / "site" / "data" / "catalog.json"
REQUIRED_SECTIONS = (
    "الهدف",
    "قبل أن تبدأ",
    "شرح المسألة",
    "القاعدة",
    "لماذا؟",
    "أمثلة متدرجة",
    "تحليل خطوة خطوة",
    "خطأ شائع",
    "تدريب موجه",
    "تدريب مستقل",
    "خلاصة للحفظ",
)
FORBIDDEN_PUBLIC_MARKERS = (
    "request_id:",
    "- confidence:",
    "- duration:",
    "انظر إلى المثال ثم طبّق القاعدة",
    "source-map.json",
    "archive-items/",
    "livres/shamela/",
    "livres/pdf/",
)


class PedagogyValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = sorted(errors)
        super().__init__("\n".join(self.errors))


@dataclass(frozen=True)
class ModuleFragment:
    order: int
    path: Path
    title: str
    text: str
    question_count: int


def validate_fragment(path: Path, order: int) -> ModuleFragment:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    h2 = re.findall(r"(?m)^##\s+(.+?)\s*$", text)
    if len(h2) != 1 or not text.startswith("## "):
        errors.append(f"{path}: exactement un titre H2 en première ligne")
    title = h2[0].strip() if h2 else ""
    expected_name = f"{order:02d}-{slug(title)}.md"
    if path.name != expected_name:
        errors.append(f"{path}: nom attendu {expected_name}")
    headings = re.findall(r"(?m)^###\s+(.+?)\s*$", text)
    expected = list(REQUIRED_SECTIONS)
    expected.append("تشخيص قبلي" if order == 1 else "مراجعة تراكمية")
    expected.append("أسئلة التحقق")
    positions = [headings.index(name) if name in headings else -1 for name in expected]
    for name, position in zip(expected, positions):
        if position < 0:
            errors.append(f"{path}: section absente {name}")
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append(f"{path}: ordre des sections invalide")
    for name in expected:
        match = re.search(
            rf"(?ms)^###\s+{re.escape(name)}\s*$\n(?P<body>.*?)(?=^###\s+|\Z)",
            text,
        )
        if match and not match.group("body").strip():
            errors.append(f"{path}: section vide {name}")
    quiz_heading = re.search(r"(?m)^###\s+أسئلة التحقق\s*$", text)
    questions = parse_questions(text[quiz_heading.end():]) if quiz_heading else []
    if not 8 <= len(questions) <= 10:
        errors.append(f"{path}: questionnaire attendu 8 إلى 10, reçu {len(questions)}")
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker in text:
            errors.append(f"{path}: marqueur interdit {marker}")
    if errors:
        raise PedagogyValidationError(errors)
    return ModuleFragment(order, path, title, text.strip(), len(questions))


def load_fragments(modules_dir: Path) -> list[ModuleFragment]:
    paths = sorted(modules_dir.glob("[0-9][0-9]-*.md"))
    fragments = [validate_fragment(path, int(path.name[:2])) for path in paths]
    orders = [fragment.order for fragment in fragments]
    if orders != list(range(1, len(fragments) + 1)):
        raise PedagogyValidationError([f"{modules_dir}: numérotation non contiguë {orders}"])
    return fragments


def assemble_fragments(
    fragments: list[ModuleFragment],
    *,
    enforce_count: bool = True,
) -> str:
    if enforce_count and not 25 <= len(fragments) <= 35:
        raise PedagogyValidationError([f"nombre de modules attendu 25 à 35, reçu {len(fragments)}"])
    return "\n\n".join(fragment.text for fragment in fragments) + "\n"
~~~

- [x] **Step 4: Vérifier GREEN**

Run :

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy.FragmentValidationTest -v
~~~

Expected: 5 tests, OK.

- [x] **Step 5: Auto-review et revue indépendante**

Écrire task-1-report.md avec RED/GREEN, fichiers et concerns. Créer package manuel des deux fichiers, dispatch reviewer lecture seule. Corriger tout Critical/Important puis re-review.

---

### Task 2: Provenance, dossiers sources, sauvegarde et CLI

**Files:**
- Modify: outils/build_pedagogical_course.py
- Modify: tests/test_ajroumiya_pedagogy.py
- Report: .superpowers/sdd/ajroumiya/task-2-report.md

**Interfaces:**
- Consumes: catalog.json, source batch JSON, source-map.json, ModuleFragment.
- Produces: validate_source_batch(), validate_source_map(), write_course(), CLI.

- [x] **Step 1: Écrire tests rouges**

Ajouter une classe ProvenanceValidationTest couvrant exactement :

~~~python
class ProvenanceValidationTest(unittest.TestCase):
    def test_batch_requires_every_lesson_in_range_once(self):
        durations = {"lesson-001": 100.0, "lesson-002": 120.0}
        batch = {
            "course_id": "ajroumiya",
            "range": [1, 2],
            "lessons": [
                {
                    "lesson_id": "lesson-001",
                    "spans": [
                        {
                            "start_seconds": 0,
                            "end_seconds": 50,
                            "kind": "teaching",
                            "topic_ar": "مقدمة",
                            "claims": ["المتن للمبتدئ"],
                            "examples": [],
                            "uncertainties": [],
                        }
                    ],
                }
            ],
        }
        with self.assertRaisesRegex(PedagogyValidationError, "lesson-002"):
            validate_source_batch(batch, durations, ["lesson-001", "lesson-002"])

    def test_source_map_rejects_span_beyond_audio(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["audio_spans"][0]["end_seconds"] = 101.0
            durations["lesson-001"] = 100.0
            with self.assertRaisesRegex(PedagogyValidationError, "hors durée"):
                validate_source_map(data, fragments, durations, root, True, True)

    def test_source_map_rejects_pending_final_status(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["verification"]["pedagogy"] = "pending"
            with self.assertRaisesRegex(PedagogyValidationError, "pending"):
                validate_source_map(data, fragments, durations, root, True, True)

    def test_source_map_rejects_study_duration_outside_contract(self):
        with TemporaryDirectory() as tmp:
            data, fragments, durations, root = complete_source_map_fixture(Path(tmp))
            data["modules"][0]["estimated_study_minutes"] = 30
            with self.assertRaisesRegex(PedagogyValidationError, "15 à 25"):
                validate_source_map(data, fragments, durations, root, True, True)

    def test_write_course_preserves_first_backup(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "cours-pedagogiques" / "ajroumiya"
            directory.mkdir(parents=True)
            (directory / "cours.md").write_text("ancienne version\n", encoding="utf-8")
            write_course(root, "ajroumiya", "nouvelle version\n")
            write_course(root, "ajroumiya", "troisième version\n")
            self.assertEqual(
                "ancienne version\n",
                (directory / "cours.before-transcript-first.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "troisième version\n",
                (directory / "cours.md").read_text(encoding="utf-8"),
            )
~~~

Ajouter ce helper de test et importer ModuleFragment, expected_module_id, load_lesson_durations, validate_source_batch, validate_source_map et write_course depuis le builder :

~~~python
def complete_source_map_fixture(root: Path):
    source_dir = root / "sources"
    source_dir.mkdir()
    (source_dir / "matn.md").write_text("متن", encoding="utf-8")
    (source_dir / "charh.md").write_text("شرح", encoding="utf-8")
    durations = {f"lesson-{index:03d}": 100.0 for index in range(1, 31)}
    fragments = []
    modules = []
    for index in range(1, 26):
        title = f"الوحدة {index}"
        fragments.append(
            ModuleFragment(
                order=index,
                path=root / f"{index:02d}.md",
                title=title,
                text=valid_text(title),
                question_count=8,
            )
        )
        modules.append(
            {
                "id": expected_module_id("ajroumiya", index, title),
                "title": title,
                "estimated_study_minutes": 20,
                "audio_spans": [
                    {
                        "lesson_id": f"lesson-{index:03d}",
                        "start_seconds": 0.0,
                        "end_seconds": 50.0,
                        "evidence": "دليل صوتي واضح",
                    }
                ],
                "matn_refs": ["sources/matn.md"],
                "charh_refs": ["sources/charh.md"],
                "verification": {
                    "transcript": "verified",
                    "grammar": "verified",
                    "arabic": "verified",
                    "pedagogy": "verified",
                },
            }
        )
    excluded = [
        {
            "lesson_id": f"lesson-{index:03d}",
            "start_seconds": 0.0,
            "end_seconds": 100.0,
            "reason": "مادة إدارية",
        }
        for index in range(26, 31)
    ]
    data = {
        "schema_version": 1,
        "course_id": "ajroumiya",
        "modules": modules,
        "excluded_spans": excluded,
    }
    return data, fragments, durations, root
~~~

- [x] **Step 2: Vérifier RED**

Run:

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy.ProvenanceValidationTest -v
~~~

Expected: import errors pour interfaces absentes.

- [x] **Step 3: Implémenter validations exactes**

Implémenter :

- load_lesson_durations() lit le cours demandé dans catalog.json et retourne id vers durée;
- validate_source_batch() exige les leçons correspondant aux positions start..end, chacune une fois, et valide kind parmi teaching, example, student_question, repetition, administrative;
- toute plage respecte 0 <= start < end <= durée;
- teaching exige topic_ar et au moins un claim;
- validate_source_map() exige course_id ajroumiya, 25 à 35 modules, durée estimée 15 à 25 minutes, mêmes IDs/titres/ordre que fragments si require_fragments, au moins un audio_span par module, au moins un matn_ref existant, charh_refs optionnel, evidence non vide, quatre statuts connus;
- chaque leçon est couverte par audio_spans ou excluded_spans avec reason non vide;
- require_verified=True exige les quatre valeurs verified;
- ID attendu : f"ajroumiya-module-{index:02d}-{slug(title)}";
- write_course() crée sauvegarde une seule fois, écrit un temporaire voisin, puis os.replace().

Ajouter CLI :

~~~text
python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-batch .superpowers/sdd/ajroumiya/source-01-10.json --expected-range 1:10
python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-source-map --allow-pending --source-map-only
python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments
python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments --require-complete
python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-only
python3 outils/build_pedagogical_course.py --identifier ajroumiya
~~~

La commande --validate-fragments accepte un ensemble sparse pendant rédaction; --require-complete exige numérotation contiguë et 25 à 35 fragments. La dernière commande sans mode valide tout, assemble, sauvegarde puis écrit cours.md. --validate-only n’écrit rien. --allow-pending est refusé hors validation.

Implémenter les fonctions avec cette logique complète :

~~~python
VALID_KINDS = {
    "teaching",
    "example",
    "student_question",
    "repetition",
    "administrative",
}
VALID_STATUSES = {"pending", "verified", "needs_review"}
VERIFICATION_KEYS = {"transcript", "grammar", "arabic", "pedagogy"}


def expected_module_id(identifier: str, index: int, title: str) -> str:
    return f"{identifier}-module-{index:02d}-{slug(title)}"


def load_lesson_durations(catalog_path: Path, identifier: str) -> dict[str, float]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    course = next((item for item in catalog["courses"] if item["id"] == identifier), None)
    if course is None:
        raise PedagogyValidationError([f"cours absent du catalogue: {identifier}"])
    return {lesson["id"]: float(lesson["duration_seconds"]) for lesson in course["lessons"]}


def _validate_span(
    span: dict[str, Any],
    durations: dict[str, float],
    context: str,
    errors: list[str],
) -> str | None:
    lesson_id = span.get("lesson_id")
    if lesson_id not in durations:
        errors.append(f"{context}: lesson_id inconnu {lesson_id}")
        return None
    try:
        start = float(span["start_seconds"])
        end = float(span["end_seconds"])
    except (KeyError, TypeError, ValueError):
        errors.append(f"{context}: bornes temporelles invalides")
        return lesson_id
    if not 0 <= start < end <= durations[lesson_id]:
        errors.append(
            f"{context}: plage hors durée {lesson_id} {start}:{end}/{durations[lesson_id]}"
        )
    return lesson_id


def validate_source_batch(
    data: dict[str, Any],
    durations: dict[str, float],
    expected_ids: list[str],
) -> None:
    errors: list[str] = []
    if data.get("course_id") != "ajroumiya":
        errors.append("batch: course_id doit être ajroumiya")
    lessons = data.get("lessons")
    if not isinstance(lessons, list):
        raise PedagogyValidationError(["batch: lessons doit être une liste"])
    actual_ids = [lesson.get("lesson_id") for lesson in lessons]
    for lesson_id in expected_ids:
        count = actual_ids.count(lesson_id)
        if count != 1:
            errors.append(f"batch: {lesson_id} attendu une fois, reçu {count}")
    for lesson_id in actual_ids:
        if lesson_id not in expected_ids:
            errors.append(f"batch: lesson_id hors plage {lesson_id}")
    for lesson in lessons:
        lesson_id = lesson.get("lesson_id")
        spans = lesson.get("spans")
        if not isinstance(spans, list) or not spans:
            errors.append(f"batch: {lesson_id} sans spans")
            continue
        for index, span in enumerate(spans, start=1):
            context = f"batch {lesson_id} span {index}"
            enriched = {"lesson_id": lesson_id, **span}
            _validate_span(enriched, durations, context, errors)
            kind = span.get("kind")
            if kind not in VALID_KINDS:
                errors.append(f"{context}: kind invalide {kind}")
            if kind == "teaching":
                if not str(span.get("topic_ar", "")).strip():
                    errors.append(f"{context}: topic_ar absent")
                claims = span.get("claims")
                if not isinstance(claims, list) or not any(str(item).strip() for item in claims):
                    errors.append(f"{context}: teaching sans claim")
            for field in ("claims", "examples", "uncertainties"):
                if not isinstance(span.get(field), list):
                    errors.append(f"{context}: {field} doit être une liste")
    if errors:
        raise PedagogyValidationError(errors)


def validate_source_map(
    data: dict[str, Any],
    fragments: list[ModuleFragment],
    durations: dict[str, float],
    root: Path,
    require_verified: bool,
    require_fragments: bool,
) -> None:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("source-map: schema_version doit être 1")
    identifier = data.get("course_id")
    if identifier != "ajroumiya":
        errors.append("source-map: course_id doit être ajroumiya")
    modules = data.get("modules")
    if not isinstance(modules, list):
        raise PedagogyValidationError(["source-map: modules doit être une liste"])
    if not 25 <= len(modules) <= 35:
        errors.append(f"source-map: modules attendu 25 à 35, reçu {len(modules)}")
    if require_fragments and len(fragments) != len(modules):
        errors.append(
            f"source-map: fragments {len(fragments)} différents des modules {len(modules)}"
        )
    covered: set[str] = set()
    for index, module in enumerate(modules, start=1):
        context = f"source-map module {index}"
        title = str(module.get("title", "")).strip()
        expected_id = expected_module_id(identifier, index, title)
        if module.get("id") != expected_id:
            errors.append(f"{context}: id attendu {expected_id}")
        minutes = module.get("estimated_study_minutes")
        if not isinstance(minutes, int) or not 15 <= minutes <= 25:
            errors.append(f"{context}: estimated_study_minutes attendu 15 à 25")
        if require_fragments and index <= len(fragments):
            fragment = fragments[index - 1]
            if fragment.order != index or fragment.title != title:
                errors.append(f"{context}: fragment ne correspond pas au titre")
        spans = module.get("audio_spans")
        if not isinstance(spans, list) or not spans:
            errors.append(f"{context}: audio_spans absent")
        else:
            for span_index, span in enumerate(spans, start=1):
                lesson_id = _validate_span(
                    span,
                    durations,
                    f"{context} span {span_index}",
                    errors,
                )
                if lesson_id:
                    covered.add(lesson_id)
                if not str(span.get("evidence", "")).strip():
                    errors.append(f"{context} span {span_index}: evidence absent")
        matn_refs = module.get("matn_refs")
        if not isinstance(matn_refs, list) or not matn_refs:
            errors.append(f"{context}: matn_refs absent")
            matn_refs = []
        charh_refs = module.get("charh_refs")
        if not isinstance(charh_refs, list):
            errors.append(f"{context}: charh_refs doit être une liste")
            charh_refs = []
        for reference in [*matn_refs, *charh_refs]:
            if not (root / reference).exists():
                errors.append(f"{context}: source absente {reference}")
        verification = module.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{context}: verification absente")
            verification = {}
        if set(verification) != VERIFICATION_KEYS:
            errors.append(f"{context}: clés verification invalides")
        for key in VERIFICATION_KEYS:
            status = verification.get(key)
            if status not in VALID_STATUSES:
                errors.append(f"{context}: statut {key} invalide {status}")
            if require_verified and status != "verified":
                errors.append(f"{context}: statut {key} non verified: {status}")
    exclusions = data.get("excluded_spans")
    if not isinstance(exclusions, list):
        errors.append("source-map: excluded_spans doit être une liste")
        exclusions = []
    for index, exclusion in enumerate(exclusions, start=1):
        context = f"source-map exclusion {index}"
        lesson_id = _validate_span(exclusion, durations, context, errors)
        if lesson_id:
            covered.add(lesson_id)
        if not str(exclusion.get("reason", "")).strip():
            errors.append(f"{context}: reason absent")
    missing = sorted(set(durations) - covered)
    extra = sorted(covered - set(durations))
    if missing:
        errors.append(f"source-map: leçons non couvertes {missing}")
    if extra:
        errors.append(f"source-map: leçons inconnues {extra}")
    if errors:
        raise PedagogyValidationError(errors)


def write_course(root: Path, identifier: str, content: str) -> Path:
    directory = root / "cours-pedagogiques" / identifier
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "cours.md"
    backup = directory / "cours.before-transcript-first.md"
    if target.exists() and not backup.exists():
        shutil.copy2(target, backup)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target


def _parse_expected_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+):(\d+)", value)
    if not match:
        raise argparse.ArgumentTypeError("format attendu START:END")
    start, end = (int(part) for part in match.groups())
    if start < 1 or end < start:
        raise argparse.ArgumentTypeError("plage invalide")
    return start, end


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--identifier", required=True)
    parser.add_argument("--validate-batch", type=Path)
    parser.add_argument("--expected-range", type=_parse_expected_range)
    parser.add_argument("--validate-source-map", action="store_true")
    parser.add_argument("--source-map-only", action="store_true")
    parser.add_argument("--validate-fragments", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    course_dir = root / "cours-pedagogiques" / args.identifier
    modules_dir = course_dir / "modules"
    catalog_path = root / "site" / "data" / "catalog.json"
    durations = load_lesson_durations(catalog_path, args.identifier)
    modes = sum(
        bool(value)
        for value in (
            args.validate_batch,
            args.validate_source_map,
            args.validate_fragments,
            args.validate_only,
        )
    )
    if modes > 1:
        parser.error("choisir un seul mode de validation")
    if args.source_map_only and not args.validate_source_map:
        parser.error("--source-map-only exige --validate-source-map")
    if args.require_complete and not args.validate_fragments:
        parser.error("--require-complete exige --validate-fragments")
    if args.allow_pending and not (args.validate_source_map or args.validate_only):
        parser.error("--allow-pending exige un mode de validation")
    if args.validate_batch:
        if not args.expected_range:
            parser.error("--expected-range requis avec --validate-batch")
        start, end = args.expected_range
        expected_ids = list(durations)[start - 1:end]
        if len(expected_ids) != end - start + 1:
            parser.error("plage hors catalogue")
        data = json.loads(args.validate_batch.read_text(encoding="utf-8"))
        if data.get("range") != [start, end]:
            raise PedagogyValidationError(["batch: range ne correspond pas à --expected-range"])
        validate_source_batch(data, durations, expected_ids)
        print(f"batch valid lessons={len(expected_ids)}")
        return
    if args.validate_fragments:
        paths = sorted(modules_dir.glob("[0-9][0-9]-*.md"))
        fragments = [validate_fragment(path, int(path.name[:2])) for path in paths]
        if args.require_complete:
            fragments = load_fragments(modules_dir)
            assemble_fragments(fragments)
        print(f"fragments valid count={len(fragments)}")
        return

    source_map = json.loads((course_dir / "source-map.json").read_text(encoding="utf-8"))
    fragments = [] if args.source_map_only else load_fragments(modules_dir)
    validate_source_map(
        source_map,
        fragments,
        durations,
        root,
        require_verified=not args.allow_pending,
        require_fragments=not args.source_map_only,
    )
    if args.validate_source_map or args.validate_only:
        print(f"source-map valid modules={len(source_map['modules'])} lessons={len(durations)}")
        return
    content = assemble_fragments(fragments)
    target = write_course(root, args.identifier, content)
    print(f"course={target.relative_to(root)} modules={len(fragments)}")


if __name__ == "__main__":
    main()
~~~

- [x] **Step 4: Vérifier GREEN et syntaxe**

Run:

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy -v
rtk proxy env PYTHONPYCACHEPREFIX=/tmp/ajroumiya-pycache python3 -m py_compile outils/build_pedagogical_course.py tests/test_ajroumiya_pedagogy.py
~~~

Expected: tous tests builder verts, syntaxe code 0.

- [x] **Step 5: Revue Task 2**

Rapport complet, package manuel, reviewer lecture seule. Aucun Critical/Important ouvert.

---

### Task 3: Baselines et ledger

**Files:**
- Create: .superpowers/sdd/ajroumiya/progress.md
- Report: .superpowers/sdd/ajroumiya/task-3-report.md

**Interfaces:**
- Consumes: état initial vérifié.
- Produces: baselines immuables utilisées Task 13.

- [x] **Step 1: Confirmer hashes exacts**

Run:

~~~text
rtk proxy sha256sum cours-pedagogiques/ajroumiya/cours.md audios-opus/manifest.tsv site/data/catalog.json
~~~

Expected:

~~~text
e56aa43b03156bbd6b379733b3ec27e5450be94c433f9adfbb13902001f3d442  cours-pedagogiques/ajroumiya/cours.md
05a32024638382fa528358b8b8b47982a2faadfb85416ac9ba58d9c2579dc469  audios-opus/manifest.tsv
56335fd8dd22f5dd2ce0e97d6e353253584342cbde29042dd145791b7b52a0a0  site/data/catalog.json
~~~

- [x] **Step 2: Calculer empreintes reproductibles**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import hashlib
from pathlib import Path

root = Path(".")


def fingerprint(paths):
    digest = hashlib.sha256()
    count = 0
    size = 0
    for path in sorted(paths, key=lambda item: item.as_posix()):
        stat = path.stat()
        relative = path.relative_to(root).as_posix()
        count += 1
        size += stat.st_size
        digest.update(f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode())
    return count, size, digest.hexdigest()


print("audios", fingerprint(Path("audios-opus").glob("*/*.opus")))
print(
    "transcriptions",
    fingerprint(
        path
        for path in Path("archive-items").glob("*/transcriptions-deepgram/*")
        if path.is_file()
    ),
)
print("pdf", fingerprint(Path("livres").rglob("*.pdf")))
print(
    "shamela",
    fingerprint(path for path in Path("livres/shamela").rglob("*") if path.is_file()),
)
PY
~~~

Expected :

~~~text
audios (792, 6976779890, '6f29c20a659eafbc7c9f9f8e7546e30c4ba43a1a3ec70148b32d3bfdb1b28678')
transcriptions (1554, 1726933840, 'd8b6702618c4fb448270b9be857c841eb32320dd7259b120429d7dbcd4ea1e27')
pdf (58, 384458721, 'ddac380587dfda0220cbfb7ac4bee87ad9b6ce38615a4becefa50ba86f726649')
shamela (179, 139212638, '99c134de914cb6e467b51a60fea0088042fd48a8e8ae9ad59f158e16814aab20')
~~~

- [x] **Step 3: Enregistrer empreintes**

Ledger exact :

~~~markdown
# Ajroumiya transcript-first progress

Spec: docs/superpowers/specs/2026-07-11-ajroumiya-transcript-first-pedagogy-design.md
Plan: docs/superpowers/plans/2026-07-11-ajroumiya-transcript-first-pedagogy.md
Status: active

Baseline cours.md: e56aa43b03156bbd6b379733b3ec27e5450be94c433f9adfbb13902001f3d442
Baseline manifest: 05a32024638382fa528358b8b8b47982a2faadfb85416ac9ba58d9c2579dc469
Baseline catalog: 56335fd8dd22f5dd2ce0e97d6e353253584342cbde29042dd145791b7b52a0a0
Baseline audios: 6f29c20a659eafbc7c9f9f8e7546e30c4ba43a1a3ec70148b32d3bfdb1b28678
Baseline transcriptions: d8b6702618c4fb448270b9be857c841eb32320dd7259b120429d7dbcd4ea1e27
Baseline PDFs: ddac380587dfda0220cbfb7ac4bee87ad9b6ce38615a4becefa50ba86f726649
Baseline Shamela: 99c134de914cb6e467b51a60fea0088042fd48a8e8ae9ad59f158e16814aab20
Baseline other courses projection: a463b9d8710bef0def8cd3abe74a7d89ea261c36037d82b81f7d3a19dea72f77

Task 1: complete after clean review
Task 2: complete after clean review
Task 3: complete after baseline confirmation
~~~

- [x] **Step 4: Vérifier état initial**

Run :

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
~~~

Expected: 31 tests existants plus tests builder, tous verts.

---

## Vague parallèle des dossiers sources — Tasks 4–6

Ces trois tâches sont indépendantes et doivent être dispatchées dans la même vague. Aucun agent ne modifie cours.md, source-map.json ou modules/.

#### Schéma obligatoire

~~~json
{
  "course_id": "ajroumiya",
  "range": [1, 10],
  "lessons": [
    {
      "lesson_id": "001-شرح المقدمة الآجرومية للأستاذ محمود الشافعي (1)",
      "spans": [
        {
          "start_seconds": 65,
          "end_seconds": 695,
          "kind": "teaching",
          "topic_ar": "منزلة الآجرومية وطريقة دراستها",
          "claims": ["الآجرومية تجمع الأصول النحوية التي يحتاج إليها المبتدئ"],
          "examples": [],
          "uncertainties": ["اسم الكتاب المساعد في آخر الدرس يحتاج مراجعة المصدر"]
        },
        {
          "start_seconds": 945,
          "end_seconds": 1405,
          "kind": "administrative",
          "topic_ar": "معلومات الدورة",
          "claims": [],
          "examples": [],
          "uncertainties": []
        }
      ]
    }
  ]
}
~~~

Chaque span utilise les timestamps des segments, conserve les formulations utiles, sépare teaching/example/student_question/repetition/administrative, et ne corrige jamais un terme incertain par intuition.

### Task 4: Audios 1–10

**Files:**
- Create: .superpowers/sdd/ajroumiya/source-01-10.json
- Report: .superpowers/sdd/ajroumiya/task-4-report.md

- [x] Lire intégralement transcriptions 001 à 010 et JSON associés quand présents.
- [x] Consulter matn 11371 et charh 21509 uniquement pour termes ambigus.
- [x] Écrire dossier conforme, dix lesson_id exacts, couverture temporelle pédagogique et exclusions.
- [x] Valider :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-batch .superpowers/sdd/ajroumiya/source-01-10.json --expected-range 1:10
~~~

Expected: batch valid lessons=10.

- [x] Reviewer indépendant vérifie fidélité de trois leçons échantillons 001, 005, 010 et cohérence du reste. Corriger tout Critical/Important.

### Task 5: Audios 11–20

**Files:**
- Create: .superpowers/sdd/ajroumiya/source-11-20.json
- Report: .superpowers/sdd/ajroumiya/task-5-report.md

- [x] Lire intégralement transcriptions 011 à 020 et JSON associés quand présents.
- [x] Consulter matn/charh pour définitions, أدوات النصب والجزم et passages ambigus.
- [x] Écrire dix lesson_id exacts avec même schéma.
- [x] Valider :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-batch .superpowers/sdd/ajroumiya/source-11-20.json --expected-range 11:20
~~~

Expected: batch valid lessons=10.
- [x] Reviewer échantillonne 011, 015, 020; zéro Critical/Important ouvert.

### Task 6: Audios 21–30

**Files:**
- Create: .superpowers/sdd/ajroumiya/source-21-30.json
- Report: .superpowers/sdd/ajroumiya/task-6-report.md

- [x] Lire intégralement transcriptions 021 à 030 et JSON associés quand présents.
- [x] Consulter matn/charh pour المنصوبات، المجرورات، التوابع et ambiguïtés.
- [x] Écrire dix lesson_id exacts avec même schéma.
- [x] Valider :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-batch .superpowers/sdd/ajroumiya/source-21-30.json --expected-range 21:30
~~~

Expected: batch valid lessons=10.
- [x] Reviewer échantillonne 021, 025, 030; zéro Critical/Important ouvert.

Après trois reviews propres, ledger marque Tasks 4–6 complete.

---

### Task 7: Architecture sémantique et tests d’acceptation rouges

**Files:**
- Create: cours-pedagogiques/ajroumiya/source-map.json
- Modify: tests/test_ajroumiya_pedagogy.py
- Create: tests/ui_ajroumiya_course.spec.js
- Report: .superpowers/sdd/ajroumiya/task-7-report.md

**Interfaces:**
- Consumes: trois dossiers sources validés.
- Produces: 25 à 35 entrées ordonnées et assignments d’écriture par index modulo 3.

- [x] **Step 1: Synthétiser plan du cours**

Fusionner spans par compétence. Pour chaque module écrire id exact, titre arabe, estimated_study_minutes entier entre 15 et 25, audio_spans avec evidence, matn_refs, charh_refs utiles, et statuts :

~~~json
{
  "transcript": "verified",
  "grammar": "pending",
  "arabic": "pending",
  "pedagogy": "pending"
}
~~~

Règles : aucun quota par audio; prérequis ordonnés; chaque leçon couverte ou exclue; 25 à 35 modules.

- [x] **Step 2: Valider source-map en mode pending**

Run:

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-source-map --allow-pending --source-map-only
~~~

Expected: source-map valid modules entre 25 et 35, lessons=30.

- [x] **Step 3: Écrire test Python d’acceptation**

Ajouter :

~~~python
class AjroumiyaFinalContractTest(unittest.TestCase):
    def test_public_course_has_transcript_first_contract(self):
        from outils.generate_site_data import load_pedagogical_modules

        modules = load_pedagogical_modules("ajroumiya")
        self.assertGreaterEqual(len(modules), 25)
        self.assertLessEqual(len(modules), 35)
        self.assertEqual(len(modules), len({module["id"] for module in modules}))
        for module in modules:
            self.assertGreaterEqual(len(module["questions"]), 8, module["title"])
            self.assertLessEqual(len(module["questions"]), 10, module["title"])
            for heading in (
                "الهدف",
                "قبل أن تبدأ",
                "شرح المسألة",
                "القاعدة",
                "لماذا؟",
                "أمثلة متدرجة",
                "تحليل خطوة خطوة",
                "خطأ شائع",
                "تدريب موجه",
                "تدريب مستقل",
                "خلاصة للحفظ",
            ):
                self.assertIn(heading, module["markdown"], (module["title"], heading))
~~~

- [x] **Step 4: Écrire test navigateur**

~~~javascript
const { test, expect } = require("@playwright/test");

test("ajroumiya exposes complete transcript-first modules", async ({ page }) => {
  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator(".course-tile").first().click();
  const modules = page.locator("#moduleGrid .module-tile");
  const count = await modules.count();
  expect(count).toBeGreaterThanOrEqual(25);
  expect(count).toBeLessThanOrEqual(35);

  for (const index of [0, Math.floor(count / 2), count - 1]) {
    await modules.nth(index).click();
    await expect(page.locator("#courseContent")).toContainText("الهدف");
    await expect(page.locator("#courseContent")).toContainText("خلاصة للحفظ");
    await page.locator('[data-tab="quiz"]').click();
    const questions = page.locator("#quizList .question-card");
    const questionCount = await questions.count();
    expect(questionCount).toBeGreaterThanOrEqual(8);
    expect(questionCount).toBeLessThanOrEqual(10);
    await questions.first().locator(".answer-toggle").click();
    await expect(questions.first().locator(".question-answer")).toBeVisible();
  }
});
~~~

- [x] **Step 5: Vérifier RED**

Run Python :

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy.AjroumiyaFinalContractTest -v
~~~

Expected: FAIL car cours actuel contient 16 modules.

Démarrer serveur dans terminal dédié :

~~~text
rtk proxy python3 -B -m http.server 8766 --bind 127.0.0.1
~~~

Run navigateur :

~~~text
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_ajroumiya_course.spec.js --browser=chromium --reporter=line --output=/tmp/cours-arabe-ajroumiya-red'
~~~

Expected: FAIL sur count=16. Arrêter serveur puis confirmer curl code 7. Le builder unitaire reste vert.

- [x] **Step 6: Revue architecture**

Reviewer lit trois batches, source-map et progression globale. Il vérifie changements de باب, couverture, doublons et prérequis. Corriger puis re-review.

---

## Vague parallèle de rédaction arabe — Tasks 8–10

Les trois agents lisent source-map.json et prennent des indices disjoints :

- Writer A : index modulo 3 égal 1.
- Writer B : index modulo 3 égal 2.
- Writer C : index modulo 3 égal 0.

Chaque fichier utilise l’index à deux chiffres, un tiret et slug(title), par exemple 01-منزلة-الآجرومية.md. L’index et le slug correspondent à source-map. Chaque module suit les treize sections, le premier utilisant تشخيص قبلي. Chaque questionnaire suit répartition 8–10 de la spec.

### Task 8: Modules Writer A

**Files:** Create only assigned cours-pedagogiques/ajroumiya/modules/*.md

- [x] Sélectionner uniquement les modules dont index modulo 3 égale 1.
- [x] Lire pour chaque module audio_spans, transcription autour des bornes, matn_refs et charh_refs.
- [x] Rédiger les treize sections en arabe simple; vocaliser exemples, citations et phrases analysées.
- [x] Construire 8–10 questions avec rappel, compréhension, classement, application, analyse, correction d’erreur, transfert et révision cumulative.
- [x] Vérifier chaque réponse : solution explicite, fonction, حكم, علامة et سبب lorsque requis.
- [x] Exécuter :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments
~~~

- [x] Écrire task-8-report.md avec liste exacte des fichiers. Aucun fichier Writer B/C modifié.

### Task 9: Modules Writer B

**Files:** Create only assigned cours-pedagogiques/ajroumiya/modules/*.md

- [x] Sélectionner uniquement les modules dont index modulo 3 égale 2.
- [x] Lire pour chaque module audio_spans, transcription autour des bornes, matn_refs et charh_refs.
- [x] Rédiger les treize sections en arabe simple; vocaliser exemples, citations et phrases analysées.
- [x] Construire 8–10 questions avec rappel, compréhension, classement, application, analyse, correction d’erreur, transfert et révision cumulative.
- [x] Vérifier chaque réponse : solution explicite, fonction, حكم, علامة et سبب lorsque requis.
- [x] Exécuter :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments
~~~

Corriger toute section ou question invalide.
- [x] Écrire task-9-report.md avec liste exacte des fichiers. Aucun fichier Writer A/C modifié.

### Task 10: Modules Writer C

**Files:** Create only assigned cours-pedagogiques/ajroumiya/modules/*.md

- [x] Sélectionner uniquement les modules dont index modulo 3 égale 0.
- [x] Lire pour chaque module audio_spans, transcription autour des bornes, matn_refs et charh_refs.
- [x] Rédiger les treize sections en arabe simple; vocaliser exemples, citations et phrases analysées.
- [x] Construire 8–10 questions avec rappel, compréhension, classement, application, analyse, correction d’erreur, transfert et révision cumulative.
- [x] Vérifier chaque réponse : solution explicite, fonction, حكم, علامة et سبب lorsque requis.
- [x] Exécuter :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments
~~~

Corriger toute section ou question invalide.
- [x] Écrire task-10-report.md avec liste exacte des fichiers. Aucun fichier Writer A/B modifié.

Après les trois retours :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-fragments --require-complete
~~~

Expected: fragments valid, count entre 25 et 35. Dispatch reviewer structure; corriger tout fichier manquant, doublon ou invalide.

---

### Task 11: Revues spécialisées et vague corrective unique

**Files:**
- Create: .superpowers/sdd/ajroumiya/review-fidelity-a.md
- Create: .superpowers/sdd/ajroumiya/review-fidelity-b.md
- Create: .superpowers/sdd/ajroumiya/review-fidelity-c.md
- Create: .superpowers/sdd/ajroumiya/review-pedagogy-a.md
- Create: .superpowers/sdd/ajroumiya/review-pedagogy-b.md
- Create: .superpowers/sdd/ajroumiya/review-pedagogy-c.md
- Modify: fragments signalés
- Modify: cours-pedagogiques/ajroumiya/source-map.json après approbation

- [x] **Wave 1: fidélité et grammaire**

Trois reviewers lecture seule, mêmes partitions A/B/C. Pour chaque module :

- chaque affirmation soutenue par audio_span;
- règle canonique conforme matn;
- charh utilisé seulement si utile;
- terme ASR incertain non propagé;
- exemples et iʿrāb corrects.

- [x] **Wave 2: pédagogie et arabe**

Trois reviewers lecture seule, partitions A/B/C. Vérifier :

- objectif observable et prérequis;
- difficulté progressive;
- explication arabe claire;
- vocalisation des exemples;
- erreur fréquente réellement plausible;
- entraînements distincts;
- 8–10 questions couvrant rappel, compréhension, classement, application, analyse, correction, transfert, cumulatif;
- réponses complètes et non génériques.

- [x] **Vague corrective**

Compiler liste exhaustive Critical/Important des six rapports. Envoyer liste entière à un seul fix-agent, fragments uniquement. Relancer validations ciblées puis mêmes reviewers. Répéter jusqu’à zéro Critical/Important.

- [x] **Consolider statuts**

Après approbations, changer grammar, arabic, pedagogy vers verified pour tous modules. Transcript reste verified depuis Task 7.

- [x] **Validation finale pending interdite**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-only
~~~

Expected: validation complète code 0, aucun pending.

---

### Task 12: Assemblage, sauvegarde et catalogue

**Files:**
- Create once: cours-pedagogiques/ajroumiya/cours.before-transcript-first.md
- Modify: cours-pedagogiques/ajroumiya/cours.md
- Modify: site/data/catalog.json
- Report: .superpowers/sdd/ajroumiya/task-12-report.md

- [x] **Step 1: Construire cours**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/build_pedagogical_course.py --identifier ajroumiya
~~~

Expected: backup created, modules 25–35, questions 8–10, cours.md written atomically.

- [x] **Step 2: Vérifier backup**

Run :

~~~text
rtk proxy sha256sum cours-pedagogiques/ajroumiya/cours.before-transcript-first.md
~~~

Expected: e56aa43b03156bbd6b379733b3ec27e5450be94c433f9adfbb13902001f3d442.

- [x] **Step 3: Régénérer catalogue**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 outils/generate_site_data.py
~~~

Expected: courses=14 lessons=792.

- [x] **Step 4: Vérifier GREEN Python**

Run :

~~~text
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ajroumiya_pedagogy -v
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
~~~

Expected: contrat final vert et suite complète verte.

- [x] **Step 5: Vérifier projection treize autres cours**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import hashlib
import json
from pathlib import Path

catalog = json.loads(Path("site/data/catalog.json").read_text(encoding="utf-8"))
other_courses = [course for course in catalog["courses"] if course["id"] != "ajroumiya"]
blob = json.dumps(
    other_courses,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode()
print(hashlib.sha256(blob).hexdigest())
PY
~~~

Expected: a463b9d8710bef0def8cd3abe74a7d89ea261c36037d82b81f7d3a19dea72f77.

- [x] **Step 6: Revue Task 12**

Reviewer compare source-map, fragments, cours.md et catalogue. Aucun Critical/Important ouvert.

---

### Task 13: Navigateur, documentation, intégrité et revue globale

**Files:**
- Modify: README.md
- Verify: tous fichiers autorisés et toutes données protégées
- Report: .superpowers/sdd/ajroumiya/task-13-report.md

- [x] **Step 1: Mettre README à jour**

Documenter :

~~~text
rtk proxy python3 outils/build_pedagogical_course.py --identifier ajroumiya --validate-only
rtk proxy python3 outils/build_pedagogical_course.py --identifier ajroumiya
~~~

Ajouter tests/ui_ajroumiya_course.spec.js à commande Playwright existante.

- [x] **Step 2: Syntaxe**

Run :

~~~text
rtk proxy env PYTHONPYCACHEPREFIX=/tmp/ajroumiya-final-pycache python3 -m py_compile outils/archive_audio_compress.py outils/generate_site_data.py outils/generate_pedagogical_courses.py outils/deepgram_archive.py outils/shamela_download.py outils/build_pedagogical_course.py tests/test_ajroumiya_pedagogy.py
rtk proxy node --check site/assets/app.js
rtk proxy node --check tests/ui_quiz.spec.js
rtk proxy node --check tests/ui_resources.spec.js
rtk proxy node --check tests/ui_transcript_race.spec.js
rtk proxy node --check tests/ui_ajroumiya_course.spec.js
rtk proxy bash -n ouvrir-site.sh
~~~

Expected: tous codes 0.

- [x] **Step 3: Browser GREEN**

Démarrer serveur 127.0.0.1:8766. agent-browser absent attendu; fallback Playwright Chromium :

~~~text
rtk proxy npx --yes -p @playwright/test@latest bash -lc 'BIN_DIR=$(dirname "$(which playwright)"); export NODE_PATH=$(dirname "$BIN_DIR"); playwright test tests/ui_quiz.spec.js tests/ui_resources.spec.js tests/ui_transcript_race.spec.js tests/ui_ajroumiya_course.spec.js --browser=chromium --reporter=line --output=/tmp/cours-arabe-ajroumiya-final'
~~~

Expected: 4 passed.

- [x] **Step 4: Catalogue**

Run :

~~~text
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import json
from pathlib import Path
from outils.generate_site_data import build_catalog

old = json.loads(Path("site/data/catalog.json").read_text(encoding="utf-8"))
new = build_catalog()
ajroumiya = next(course for course in new["courses"] if course["id"] == "ajroumiya")
question_counts = [len(module["questions"]) for module in ajroumiya["modules"]]
print(
    {
        "equal": old == new,
        "courses": new["course_count"],
        "lessons": new["lesson_count"],
        "modules": len(ajroumiya["modules"]),
        "questions_min": min(question_counts),
        "questions_max": max(question_counts),
    }
)
PY
~~~

Expected: equal=True, courses=14, lessons=792, modules entre 25 et 35, questions_min >= 8, questions_max <= 10.

- [x] **Step 5: Intégrité**

Run :

~~~text
rtk proxy sha256sum audios-opus/manifest.tsv
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import hashlib
import json
from pathlib import Path

root = Path(".")


def fingerprint(paths):
    digest = hashlib.sha256()
    count = 0
    size = 0
    for path in sorted(paths, key=lambda item: item.as_posix()):
        stat = path.stat()
        relative = path.relative_to(root).as_posix()
        count += 1
        size += stat.st_size
        digest.update(f"{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode())
    return count, size, digest.hexdigest()


print("audios", fingerprint(Path("audios-opus").glob("*/*.opus")))
print(
    "transcriptions",
    fingerprint(
        path
        for path in Path("archive-items").glob("*/transcriptions-deepgram/*")
        if path.is_file()
    ),
)
print("pdf", fingerprint(Path("livres").rglob("*.pdf")))
print(
    "shamela",
    fingerprint(path for path in Path("livres/shamela").rglob("*") if path.is_file()),
)
catalog = json.loads(Path("site/data/catalog.json").read_text(encoding="utf-8"))
other_courses = [course for course in catalog["courses"] if course["id"] != "ajroumiya"]
blob = json.dumps(
    other_courses,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode()
print("other_courses", hashlib.sha256(blob).hexdigest())
PY
~~~

Confirmer :

- manifest SHA-256 05a32024638382fa528358b8b8b47982a2faadfb85416ac9ba58d9c2579dc469;
- audios fingerprint 6f29c20a659eafbc7c9f9f8e7546e30c4ba43a1a3ec70148b32d3bfdb1b28678;
- transcriptions fingerprint d8b6702618c4fb448270b9be857c841eb32320dd7259b120429d7dbcd4ea1e27;
- PDF fingerprint ddac380587dfda0220cbfb7ac4bee87ad9b6ce38615a4becefa50ba86f726649;
- Shamela fingerprint 99c134de914cb6e467b51a60fea0088042fd48a8e8ae9ad59f158e16814aab20;
- projection autres cours a463b9d8710bef0def8cd3abe74a7d89ea261c36037d82b81f7d3a19dea72f77.

- [x] **Step 6: Arrêter serveur**

curl final doit retourner code 7; ss ne montre aucun listener 8766.

- [x] **Step 7: Revue globale**

Dispatch senior reviewer lecture seule avec spec, plan, rapports, source-map, fragments et package manuel. Corriger tout Critical/Important avec un seul fix-agent puis re-review.

- [x] **Step 8: Clôturer**

Ledger : Status complete. Plan : toutes cases cochées. Projet non-Git : changements laissés en place, zéro commit. Remettre Ajroumiya complet à l’utilisateur; ne toucher aucun autre cours avant sa validation.
