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
VALID_KINDS = {
    "teaching",
    "example",
    "student_question",
    "uncertain_fragment",
    "repetition",
    "administrative",
}
VALID_STATUSES = {"pending", "verified", "needs_review"}
VERIFICATION_KEYS = {"transcript", "grammar", "arabic", "pedagogy"}
FRAGMENT_FILE_RE = re.compile(r"^(?P<order>\d{2,3})-.+\.md$")


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


def discover_fragment_files(modules_dir: Path) -> list[tuple[int, Path]]:
    indexed_paths = []
    for path in modules_dir.glob("*.md"):
        match = FRAGMENT_FILE_RE.fullmatch(path.name)
        if match:
            indexed_paths.append((int(match.group("order")), path))
    return sorted(indexed_paths, key=lambda item: (item[0], item[1].name))


def load_fragments(modules_dir: Path) -> list[ModuleFragment]:
    fragments = [
        validate_fragment(path, order)
        for order, path in discover_fragment_files(modules_dir)
    ]
    orders = [fragment.order for fragment in fragments]
    if orders != list(range(1, len(fragments) + 1)):
        raise PedagogyValidationError([f"{modules_dir}: numérotation non contiguë {orders}"])
    return fragments


def module_count_range(data: dict[str, Any]) -> tuple[int, int]:
    value = data.get("module_count_range")
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(bound) is not int for bound in value)
    ):
        raise PedagogyValidationError(
            ["source-map: module_count_range doit être une liste de deux entiers"]
        )
    minimum, maximum = value
    if minimum < 1 or maximum < minimum:
        raise PedagogyValidationError(["source-map: module_count_range invalide"])
    return minimum, maximum


def assemble_fragments(
    fragments: list[ModuleFragment],
    *,
    enforce_count: bool = True,
    count_range: tuple[int, int] = (25, 35),
) -> str:
    minimum, maximum = count_range
    if enforce_count and not minimum <= len(fragments) <= maximum:
        raise PedagogyValidationError(
            [f"nombre de modules attendu {minimum} à {maximum}, reçu {len(fragments)}"]
        )
    return "\n\n".join(fragment.text for fragment in fragments) + "\n"


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
    course_id: str,
) -> None:
    errors: list[str] = []
    if data.get("course_id") != course_id:
        errors.append(f"batch: course_id doit être {course_id}")
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
    expected_identifier: str,
) -> None:
    errors: list[str] = []
    if data.get("schema_version") != 2:
        errors.append("source-map: schema_version doit être 2")
    identifier = data.get("course_id")
    if identifier != expected_identifier:
        errors.append(f"source-map: course_id doit être {expected_identifier}")
    try:
        minimum, maximum = module_count_range(data)
    except PedagogyValidationError as exc:
        errors.extend(exc.errors)
        minimum, maximum = (0, -1)
    inventory = data.get("source_inventory")
    if not isinstance(inventory, dict):
        errors.append("source-map: source_inventory doit être un objet")
        canonical_available = None
    else:
        canonical_available = inventory.get("canonical_available")
        if type(canonical_available) is not bool:
            errors.append("source-map: source_inventory canonical_available doit être booléen")
    modules = data.get("modules")
    if not isinstance(modules, list):
        raise PedagogyValidationError(["source-map: modules doit être une liste"])
    if not minimum <= len(modules) <= maximum:
        errors.append(
            f"source-map: modules attendu {minimum} à {maximum}, reçu {len(modules)}"
        )
    if require_fragments and not minimum <= len(fragments) <= maximum:
        errors.append(
            f"source-map: fragments attendu {minimum} à {maximum}, reçu {len(fragments)}"
        )
    if require_fragments and len(fragments) != len(modules):
        errors.append(
            f"source-map: fragments {len(fragments)} différents des modules {len(modules)}"
        )
    covered: set[str] = set()
    for index, module in enumerate(modules, start=1):
        context = f"source-map module {index}"
        title = str(module.get("title", "")).strip()
        expected_id = expected_module_id(expected_identifier, index, title)
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
        canonical_refs = module.get("canonical_refs")
        if "canonical_refs" not in module:
            errors.append(f"{context}: canonical_refs absent")
        if not isinstance(canonical_refs, list):
            errors.append(f"{context}: canonical_refs doit être une liste")
            canonical_refs = []
        elif canonical_available is not False and not canonical_refs:
            errors.append(f"{context}: canonical_refs absent")
        elif canonical_available is False and canonical_refs:
            errors.append(f"{context}: canonical_refs contredit source_inventory")
        supporting_refs = module.get("supporting_refs")
        if "supporting_refs" not in module:
            errors.append(f"{context}: supporting_refs absent")
        if not isinstance(supporting_refs, list):
            errors.append(f"{context}: supporting_refs doit être une liste")
            supporting_refs = []
        for reference in [*canonical_refs, *supporting_refs]:
            if not isinstance(reference, str) or not reference.strip():
                errors.append(f"{context}: référence source invalide")
            elif not (root / reference).exists():
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
        validate_source_batch(data, durations, expected_ids, args.identifier)
        print(f"batch valid lessons={len(expected_ids)}")
        return
    if args.validate_fragments:
        fragments = [
            validate_fragment(path, order)
            for order, path in discover_fragment_files(modules_dir)
        ]
        if args.require_complete:
            fragments = load_fragments(modules_dir)
            source_map = json.loads((course_dir / "source-map.json").read_text(encoding="utf-8"))
            assemble_fragments(fragments, count_range=module_count_range(source_map))
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
        expected_identifier=args.identifier,
    )
    if args.validate_source_map or args.validate_only:
        print(f"source-map valid modules={len(source_map['modules'])} lessons={len(durations)}")
        return
    content = assemble_fragments(fragments, count_range=module_count_range(source_map))
    target = write_course(root, args.identifier, content)
    print(f"course={target.relative_to(root)} modules={len(fragments)}")


if __name__ == "__main__":
    main()
